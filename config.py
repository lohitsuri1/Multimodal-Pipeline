"""Configuration management for devotional video pipeline."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for devotional video generation."""
    
    # Base directories
    BASE_DIR = Path(__file__).parent
    OUTPUT_DIR = BASE_DIR / os.getenv("OUTPUT_DIR", "output_videos")
    TEMP_DIR = BASE_DIR / os.getenv("TEMP_DIR", "temp_files")
    CACHE_DIR = BASE_DIR / os.getenv("CACHE_DIR", ".cache")
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

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

    # -----------------------------------------------------------------------
    # Cost controls
    # -----------------------------------------------------------------------
    MAX_TOKENS_PER_CALL = int(os.getenv("MAX_TOKENS_PER_CALL", "4000"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    MAX_SCENES_PER_RUN = int(os.getenv("MAX_SCENES_PER_RUN", "30"))
    MAX_TTS_CHARS = int(os.getenv("MAX_TTS_CHARS", "5000"))
    
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
        
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set in .env file")
        
        # PEXELS or PIXABAY key is needed for visuals
        if not cls.PEXELS_API_KEY and not cls.PIXABAY_API_KEY:
            errors.append("Either PEXELS_API_KEY or PIXABAY_API_KEY must be set in .env file")
        
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
            "elevenlabs": cls.ELEVENLABS_API_KEY,
            "pexels": cls.PEXELS_API_KEY,
            "pixabay": cls.PIXABAY_API_KEY,
        }
