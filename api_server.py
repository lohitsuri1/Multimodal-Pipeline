"""FastAPI server for the Multimodal Pipeline.

Features
--------
- Optional API-key authentication via the ``X-API-Key`` header.
  Enabled by setting the ``API_KEY`` environment variable.
- In-memory rate limiting (per client IP, configurable via ``RATE_LIMIT_PER_MINUTE``).
- Endpoint to generate long-form scripts and/or shorts for a given preset.
- ``/health`` endpoint for uptime checks.

Usage
-----
    uvicorn api_server:app --reload

Environment variables
---------------------
    API_KEY               — If set, every request must include X-API-Key: <value>.
    RATE_LIMIT_PER_MINUTE — Requests allowed per IP per minute (default 10).
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import Config
from content_presets import get_preset
from llm_client import call_llm
from pipeline_cache import get_cached, make_cache_key, set_cached
from shorts_extractor import extract_shorts, shorts_dry_run_estimate

app = FastAPI(
    title="Multimodal Pipeline API",
    description="Generate faceless video scripts and shorts for YouTube & Instagram.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# In-memory rate-limiting state
# ---------------------------------------------------------------------------
_request_log: Dict[str, List[float]] = defaultdict(list)


# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------

def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def check_api_key(request: Request) -> None:
    """Raise 401 if API_KEY is configured and the header does not match."""
    if Config.API_KEY:
        provided = request.headers.get("X-API-Key", "")
        if provided != Config.API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API key.")


def check_rate_limit(request: Request) -> None:
    """Raise 429 if the client has exceeded RATE_LIMIT_PER_MINUTE."""
    ip = _get_client_ip(request)
    now = time.time()
    window = 60.0
    limit = Config.RATE_LIMIT_PER_MINUTE

    # Drop timestamps outside the rolling window
    _request_log[ip] = [t for t in _request_log[ip] if now - t < window]

    if len(_request_log[ip]) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {limit} requests per minute.",
        )
    _request_log[ip].append(now)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    preset: str = Field("devotional", description="Preset name: finance_ai_saas | devotional")
    theme: Optional[str] = Field(None, description="Topic / theme for this video")
    output: str = Field("both", description="What to generate: long | shorts | both")
    tier: str = Field("free", description="Quality tier: free | low_cost | hq")
    shorts_count: int = Field(4, ge=1, le=8, description="Number of shorts to extract")
    dry_run: bool = Field(False, description="Estimate usage without calling paid APIs")


class ShortItem(BaseModel):
    title: str
    hook: str
    body: str
    cta: str
    caption_text: str
    broll_keywords: List[str]
    source_section: str
    estimated_words: int


class GenerateResponse(BaseModel):
    preset: str
    theme: str
    tier: str
    dry_run: bool
    long_script: Optional[str] = None
    titles: Optional[List[str]] = None
    thumbnail_texts: Optional[List[str]] = None
    platform_cues: Optional[Dict[str, str]] = None
    shorts: Optional[List[ShortItem]] = None
    dry_run_estimate: Optional[Dict] = None
    cached: bool = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _openai_generate(system: str, user: str, max_tokens: int = None) -> str:
    """Call the configured LLM and return the assistant message."""
    return call_llm(
        system=system,
        user=user,
        model="gpt-4",
        max_tokens=max_tokens or Config.MAX_TOKENS_PER_CALL,
    )


def _parse_numbered_list(text: str) -> List[str]:
    """Extract items from a numbered list (1. … / 1) … / - …)."""
    items = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove leading number / bullet
        cleaned = line.lstrip("0123456789.-) ")
        if cleaned:
            items.append(cleaned)
    return items[:3]  # cap at 3


def _words_per_minute(tier: str) -> int:
    """Return approximate narration words-per-minute for a tier."""
    return {"free": 130, "low_cost": 140, "hq": 150}.get(tier, 130)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health() -> Dict:
    return {"status": "ok"}


@app.post("/api/generate", response_model=GenerateResponse)
def generate(
    body: GenerateRequest,
    _auth: None = Depends(check_api_key),
    _rate: None = Depends(check_rate_limit),
) -> GenerateResponse:
    """
    Generate long-form script and/or shorts for the requested preset & theme.

    - Set ``dry_run=true`` to estimate usage without hitting paid APIs.
    - Results are cached on disk; identical requests are served from cache.
    """
    preset = get_preset(body.preset)
    theme = body.theme or preset.default_themes[0]
    duration = Config.VIDEO_DURATION_MINUTES
    wpm = _words_per_minute(body.tier)

    cache_key = make_cache_key(
        preset=body.preset,
        theme=theme,
        output=body.output,
        tier=body.tier,
        shorts_count=body.shorts_count,
        duration=duration,
    )

    # ---- Dry-run: no paid API calls ----------------------------------------
    if body.dry_run:
        est: Dict = {"preset": body.preset, "theme": theme, "tier": body.tier}
        if body.output in ("long", "both"):
            target_words = duration * wpm
            est["long_script_estimated_tokens"] = int(target_words * 1.4)
            est["long_script_api_calls"] = 1
            est["title_api_calls"] = 1
            est["thumbnail_api_calls"] = 1
        if body.output in ("shorts", "both"):
            est["shorts_estimate"] = shorts_dry_run_estimate(
                {"full_script": "", "segments": []}, count=body.shorts_count
            )
        est["total_estimated_api_calls"] = sum(
            v for k, v in est.items() if k.endswith("_calls")
        )
        return GenerateResponse(
            preset=body.preset,
            theme=theme,
            tier=body.tier,
            dry_run=True,
            dry_run_estimate=est,
        )

    # ---- Serve from cache if available -------------------------------------
    cached_result = get_cached(cache_key, "api_responses")
    if cached_result:
        return GenerateResponse(**{**cached_result, "cached": True})

    # ---- Validate API key availability -------------------------------------
    if not Config.OPENAI_API_KEY and not Config.GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Neither OPENAI_API_KEY nor GOOGLE_API_KEY is configured on the server.",
        )

    result: Dict = {
        "preset": body.preset,
        "theme": theme,
        "tier": body.tier,
        "dry_run": False,
        "cached": False,
    }

    # ---- Long-form script ---------------------------------------------------
    if body.output in ("long", "both"):
        user_prompt = preset.long_form_user_template.format(
            theme=theme,
            duration_minutes=duration,
            words_per_minute=wpm,
        )
        script_text = _openai_generate(
            preset.long_form_system_prompt,
            user_prompt,
            max_tokens=Config.MAX_TOKENS_PER_CALL,
        )
        result["long_script"] = script_text
        result["platform_cues"] = preset.platform_cues

        # Titles
        title_text = _openai_generate(
            "You are a YouTube title specialist.",
            preset.title_prompt_template.format(theme=theme),
            max_tokens=200,
        )
        result["titles"] = _parse_numbered_list(title_text)

        # Thumbnail texts
        thumb_text = _openai_generate(
            "You are a YouTube thumbnail copy specialist.",
            preset.thumbnail_prompt_template.format(theme=theme),
            max_tokens=150,
        )
        result["thumbnail_texts"] = _parse_numbered_list(thumb_text)

    # ---- Shorts extraction --------------------------------------------------
    if body.output in ("shorts", "both"):
        long_script = result.get("long_script", "")
        if not long_script and body.output == "shorts":
            raise HTTPException(
                status_code=400,
                detail="Cannot extract shorts without a long script. Use output='both'.",
            )
        script_data = {"full_script": long_script, "segments": []}
        shorts_list = extract_shorts(script_data, count=body.shorts_count, preset=preset)
        result["shorts"] = shorts_list

    # ---- Persist to cache ---------------------------------------------------
    set_cached(cache_key, result, "api_responses")

    return GenerateResponse(**result)
