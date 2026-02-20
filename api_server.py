"""FastAPI server with header-based API key authentication and rate limiting.

Start the server:
    uvicorn api_server:app --reload

Environment variables required:
    PIPELINE_API_KEY   – shared secret sent by clients in the X-API-Key header.
    RATE_LIMIT_PER_MINUTE – max requests per API key per minute (default 10).
"""
import time
from collections import defaultdict
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import Config

app = FastAPI(
    title="Multimodal Pipeline API",
    description=(
        "API for generating faceless video content for YouTube and Instagram. "
        "All endpoints (except /health) require an X-API-Key header."
    ),
    version="1.0.0",
)

# In-memory rate-limit store: {api_key: [request_timestamp, ...]}
# NOTE: This is a single-process in-memory store. For multi-worker deployments
# replace with a thread-safe external store (e.g. Redis + slowapi).
_rate_store: dict = defaultdict(list)


# ──────────────────────────────────────────
# Auth & rate-limiting dependencies
# ──────────────────────────────────────────

def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Verify the API key supplied in the ``X-API-Key`` header."""
    if not Config.API_KEY:
        raise HTTPException(
            status_code=503,
            detail=(
                "API key authentication is not configured on this server. "
                "Set PIPELINE_API_KEY in .env."
            ),
        )
    if x_api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    return x_api_key


def check_rate_limit(api_key: str = Depends(verify_api_key)) -> str:
    """Enforce a per-key rolling-window rate limit (1-minute window)."""
    now = time.time()
    window_start = now - 60.0

    # Evict expired timestamps
    _rate_store[api_key] = [t for t in _rate_store[api_key] if t > window_start]

    if len(_rate_store[api_key]) >= Config.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Rate limit exceeded. "
                f"Max {Config.RATE_LIMIT_PER_MINUTE} requests per minute."
            ),
        )

    _rate_store[api_key].append(now)
    return api_key


# ──────────────────────────────────────────
# Request / Response models
# ──────────────────────────────────────────

class GenerateRequest(BaseModel):
    channel: str = "B"        # "A" (finance) or "B" (devotion)
    output_type: str = "both"  # "long" | "shorts" | "both"
    theme: Optional[str] = None
    num_shorts: int = 4
    dry_run: bool = False


class ShortsRequest(BaseModel):
    script: str
    num_shorts: int = 4


class ShortSegment(BaseModel):
    title: str
    hook: str
    script: str
    caption: str
    hashtags: List[str]
    format: str
    max_duration_seconds: int


# ──────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────

@app.get("/health", tags=["Monitoring"])
def health_check():
    """Health check – no authentication required."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/api/presets", tags=["Presets"])
def list_presets(_: str = Depends(check_rate_limit)):
    """List all available channel presets."""
    from channel_presets import CHANNEL_A_FINANCE, CHANNEL_B_DEVOTION

    return {
        "presets": [
            {
                "id": CHANNEL_A_FINANCE.channel_id,
                "name": CHANNEL_A_FINANCE.name,
                "niche": CHANNEL_A_FINANCE.niche,
                "topics_count": len(CHANNEL_A_FINANCE.topics),
            },
            {
                "id": CHANNEL_B_DEVOTION.channel_id,
                "name": CHANNEL_B_DEVOTION.name,
                "niche": CHANNEL_B_DEVOTION.niche,
                "topics_count": len(CHANNEL_B_DEVOTION.topics),
            },
        ]
    }


@app.post("/api/estimate", tags=["Content"])
def estimate_cost(
    request: GenerateRequest,
    _: str = Depends(check_rate_limit),
):
    """Return a dry-run cost estimate for a content generation run."""
    from channel_presets import get_preset
    from cli import estimate_costs

    try:
        preset = get_preset(request.channel)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    costs = estimate_costs(preset, request.output_type, "free", request.num_shorts)
    return {"channel": preset.name, "theme": request.theme, "cost_estimate": costs}


@app.post("/api/generate/titles", tags=["Content"])
def generate_titles(
    request: GenerateRequest,
    _: str = Depends(check_rate_limit),
):
    """Generate title and thumbnail text options for a video topic."""
    from channel_presets import get_preset
    from shorts_extractor import ShortsExtractor

    Config.validate_config()

    try:
        preset = get_preset(request.channel)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not request.theme:
        raise HTTPException(
            status_code=400, detail="'theme' is required for title generation."
        )

    try:
        extractor = ShortsExtractor()
        result = extractor.generate_titles_and_thumbnails(
            request.theme, preset.system_prompt
        )
        return {"channel": preset.name, "theme": request.theme, "result": result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/generate/shorts", tags=["Content"])
def generate_shorts(
    request: ShortsRequest,
    _: str = Depends(check_rate_limit),
):
    """Extract short segments from a provided long-form script."""
    from shorts_extractor import ShortsExtractor

    Config.validate_config()

    if not request.script.strip():
        raise HTTPException(status_code=400, detail="'script' cannot be empty.")

    try:
        extractor = ShortsExtractor()
        shorts = extractor.extract_shorts(request.script, num_shorts=request.num_shorts)
        return {"num_shorts": len(shorts), "shorts": shorts}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
