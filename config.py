"""Configuration management for the multimodal content pipeline."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the content generation pipeline."""

    # Base directories
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output_videos")
    TEMP_DIR = BASE_DIR / os.getenv("TEMP_DIR", "temp_files")
    CACHE_DIR = BASE_DIR / os.getenv("CACHE_DIR", ".cache")
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

    # LLM provider order (comma-separated; first available provider is tried first)
    LLM_PROVIDER_ORDER = os.getenv("LLM_PROVIDER_ORDER", "openai,gemini")

    # Visual provider order (comma-separated; first available provider is tried first)
    VISUAL_PROVIDER_ORDER = os.getenv("VISUAL_PROVIDER_ORDER", "google,pexels,pixabay")
    GOOGLE_IMAGE_MODEL = os.getenv("GOOGLE_IMAGE_MODEL", "gemini-2.0-flash-preview-image-generation")

    # API server auth & rate limiting
    API_KEY = os.getenv("API_KEY")                       # optional; set to protect endpoints
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    
    # Video settings
    VIDEO_DURATION_MINUTES = int(os.getenv("VIDEO_DURATION_MINUTES", "30"))
    VIDEO_DURATION_SECONDS = VIDEO_DURATION_MINUTES * 60
    VIDEO_WIDTH = 1920
    VIDEO_HEIGHT = 1080
    VIDEO_FPS = 30

    # Audio settings
    VOICE_LANGUAGE = os.getenv("VOICE_LANGUAGE", "en")
    VOICE_SPEED = float(os.getenv("VOICE_SPEED", "0.9"))
    MUSIC_VOLUME = float(os.getenv("MUSIC_VOLUME", "0.2"))
    MUSIC_DUCK_DB = float(os.getenv("MUSIC_DUCK_DB", "6.0"))
    MUSIC_FADE_MS = int(os.getenv("MUSIC_FADE_MS", "2500"))

    # Optional YouTube music fallback (royalty-free links only)
    MUSIC_YOUTUBE_URL = os.getenv("MUSIC_YOUTUBE_URL", "").strip()
    MUSIC_YOUTUBE_START_SEC = int(os.getenv("MUSIC_YOUTUBE_START_SEC", "0"))
    MUSIC_YOUTUBE_DURATION_SEC = int(os.getenv("MUSIC_YOUTUBE_DURATION_SEC", "0"))

    # Video polish controls
    SUBTITLES_ENABLED = os.getenv("SUBTITLES_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
    SUBTITLE_MAX_CHARS = int(os.getenv("SUBTITLE_MAX_CHARS", "80"))
    SUBTITLE_MIN_SECONDS = float(os.getenv("SUBTITLE_MIN_SECONDS", "2.0"))
    TRANSITION_SECONDS = float(os.getenv("TRANSITION_SECONDS", "0.6"))

    # -----------------------------------------------------------------------
    # Cost controls
    # -----------------------------------------------------------------------
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", os.getenv("MAX_TOKENS_PER_CALL", "4000")))
    MAX_TOKENS_PER_CALL = int(os.getenv("MAX_TOKENS_PER_CALL", "4000"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    MAX_IMAGES = int(os.getenv("MAX_IMAGES", os.getenv("MAX_SCENES_PER_RUN", "30")))
    MAX_SCENES_PER_RUN = int(os.getenv("MAX_SCENES_PER_RUN", "30"))
    MAX_TTS_CHARS = int(os.getenv("MAX_TTS_CHARS", "5000"))
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").strip().lower() in {"1", "true", "yes", "on"}
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        cls.TEMP_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration."""
        errors = []

        if not cls.OPENAI_API_KEY and not cls.GOOGLE_API_KEY:
            errors.append("Either OPENAI_API_KEY or GOOGLE_API_KEY must be set in .env file")

        # At least one visual source must be configured
        if not cls.GOOGLE_API_KEY and not cls.PEXELS_API_KEY and not cls.PIXABAY_API_KEY:
            errors.append(
                "At least one visual provider key must be set: "
                "GOOGLE_API_KEY or PEXELS_API_KEY or PIXABAY_API_KEY"
            )

        if errors:
            raise ValueError(
                "Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
            )

        return True

    @classmethod
    def get_api_keys(cls):
        """Return dictionary of available API keys."""
        return {
            "openai": cls.OPENAI_API_KEY,
            "google": cls.GOOGLE_API_KEY,
            "elevenlabs": cls.ELEVENLABS_API_KEY,
            "pexels": cls.PEXELS_API_KEY,
            "pixabay": cls.PIXABAY_API_KEY,
            "google_image_model": cls.GOOGLE_IMAGE_MODEL,
        }

    @classmethod
    def get_guardrails(cls) -> dict:
        """Return active cost-guardrail settings."""
        return {
            "max_tokens": cls.MAX_TOKENS,
            "max_images": cls.MAX_IMAGES,
            "max_tts_chars": cls.MAX_TTS_CHARS,
            "max_retries": cls.MAX_RETRIES,
            "enable_cache": cls.ENABLE_CACHE,
        }
