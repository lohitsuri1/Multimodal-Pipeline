"""FastAPI server for the Multimodal Content Pipeline.

Provides REST endpoints to trigger script generation and check pipeline status.
Includes rate limiting (via slowapi) and optional HTTP Basic Auth to
prevent abuse and runaway API costs.

Run:
    uvicorn api:app --host 0.0.0.0 --port 8000

Environment variables:
    RATE_LIMIT      – slowapi limit string, e.g. "10/minute" (default)
    API_USERNAME    – set to enable HTTP Basic Auth (leave empty to disable)
    API_PASSWORD    – required if API_USERNAME is set
"""
import secrets
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config import Config
from presets import list_niches, list_tiers, NICHE_PRESETS, COST_TIERS, OUTPUT_FORMATS
from script_generator import ContentScriptGenerator

# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address, default_limits=[Config.RATE_LIMIT])
app = FastAPI(
    title="Multimodal Content Pipeline API",
    description=(
        "Generate monetizable YouTube scripts and shorts for Finance, AI/SaaS, "
        "Passive Income, and Devotion niches."
    ),
    version="1.0.0",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# Optional HTTP Basic Auth
# ---------------------------------------------------------------------------
_security = HTTPBasic(auto_error=False)


def _check_auth(credentials: Optional[HTTPBasicCredentials] = Depends(_security)):
    """Validate HTTP Basic Auth when API_USERNAME / API_PASSWORD are configured."""
    expected_user = Config.API_USERNAME
    expected_pass = Config.API_PASSWORD

    # Auth is disabled when no username is configured
    if not expected_user:
        return

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not expected_pass:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_PASSWORD must be set when API_USERNAME is configured",
        )

    user_ok = secrets.compare_digest(
        credentials.username.encode(), expected_user.encode()
    )
    pass_ok = secrets.compare_digest(
        credentials.password.encode(), expected_pass.encode()
    )
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class GenerateRequest(BaseModel):
    niche: str = Config.DEFAULT_NICHE
    output_type: str = "both"
    cost_tier: str = Config.DEFAULT_COST_TIER
    theme: Optional[str] = None
    dry_run: bool = False


class GenerateResponse(BaseModel):
    status: str
    result: Dict[str, Any]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", tags=["info"])
@limiter.limit(Config.RATE_LIMIT)
async def root(request: Request):
    """Pipeline health check and summary."""
    return {
        "service": "Multimodal Content Pipeline",
        "status": "ok",
        "niches": list_niches(),
        "cost_tiers": list_tiers(),
        "output_formats": list(OUTPUT_FORMATS.keys()),
        "rate_limit": Config.RATE_LIMIT,
        "auth_enabled": bool(Config.API_USERNAME),
    }


@app.get("/niches", tags=["info"])
@limiter.limit(Config.RATE_LIMIT)
async def get_niches(request: Request, _: None = Depends(_check_auth)):
    """List available niche presets."""
    return {
        key: {
            "name": p["name"],
            "description": p["description"],
            "themes": p["themes"],
            "shorts_count": p["shorts"]["count"],
            "long_form_duration_minutes": p["long_form"]["duration_minutes"],
        }
        for key, p in NICHE_PRESETS.items()
    }


@app.get("/tiers", tags=["info"])
@limiter.limit(Config.RATE_LIMIT)
async def get_tiers(request: Request, _: None = Depends(_check_auth)):
    """List available cost tiers with estimated costs."""
    return COST_TIERS


@app.post("/generate", response_model=GenerateResponse, tags=["pipeline"])
@limiter.limit(Config.RATE_LIMIT)
async def generate_script(
    request: Request,
    body: GenerateRequest,
    _: None = Depends(_check_auth),
):
    """
    Generate a script (and optionally shorts) for the requested niche.

    Set `dry_run=true` to get a cost estimate without calling paid APIs.
    """
    if body.niche not in list_niches():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown niche '{body.niche}'. Valid: {list_niches()}",
        )
    if body.output_type not in OUTPUT_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown output_type '{body.output_type}'. Valid: {list(OUTPUT_FORMATS)}",
        )
    if body.cost_tier not in list_tiers():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown cost_tier '{body.cost_tier}'. Valid: {list_tiers()}",
        )

    try:
        gen = ContentScriptGenerator(
            niche=body.niche,
            cost_tier=body.cost_tier,
            output_format=body.output_type,
            dry_run=body.dry_run,
        )
        result = gen.generate(theme=body.theme)
        return GenerateResponse(status="ok", result=result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )


@app.post("/estimate", tags=["pipeline"])
@limiter.limit(Config.RATE_LIMIT)
async def estimate_cost(
    request: Request,
    body: GenerateRequest,
    _: None = Depends(_check_auth),
):
    """Estimate token usage and API cost without making any paid API calls."""
    body.dry_run = True
    return await generate_script(request, body, _)
