"""File-based cache to avoid re-billing for repeated API calls.

Caches scripts, titles, and TTS output by a stable SHA-256 hash of
their input parameters, so re-running the pipeline with identical
settings does not make additional paid API calls.
"""
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any, Optional


class CacheManager:
    """Transparent file-based cache for pipeline outputs."""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Key helpers
    # ------------------------------------------------------------------

    def _make_key(self, inputs: dict) -> str:
        """Return a 16-char hex key derived from a stable hash of *inputs*."""
        serialized = json.dumps(inputs, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()[:16]

    # ------------------------------------------------------------------
    # JSON (scripts, titles, metadata)
    # ------------------------------------------------------------------

    def get(self, inputs: dict, namespace: str = "default") -> Optional[Any]:
        """Retrieve a cached JSON value, or *None* if not present."""
        key = self._make_key(inputs)
        cache_file = self.cache_dir / namespace / f"{key}.json"
        if cache_file.exists():
            with open(cache_file) as fh:
                return json.load(fh)
        return None

    def set(self, inputs: dict, value: Any, namespace: str = "default") -> None:
        """Persist *value* (must be JSON-serialisable) under *inputs* key."""
        key = self._make_key(inputs)
        ns_dir = self.cache_dir / namespace
        ns_dir.mkdir(parents=True, exist_ok=True)
        cache_file = ns_dir / f"{key}.json"
        with open(cache_file, "w") as fh:
            json.dump(value, fh)

    # ------------------------------------------------------------------
    # Binary (TTS audio files)
    # ------------------------------------------------------------------

    def get_tts_path(self, text: str, voice_config: dict) -> Optional[Path]:
        """Return cached TTS audio path, or *None* if not cached."""
        key = self._make_key({"text": text, **voice_config})
        audio_file = self.cache_dir / "tts" / f"{key}.mp3"
        return audio_file if audio_file.exists() else None

    def get_tts_cache_path(self, text: str, voice_config: dict) -> Path:
        """Return the target path where TTS audio should be written to cache."""
        key = self._make_key({"text": text, **voice_config})
        tts_dir = self.cache_dir / "tts"
        tts_dir.mkdir(parents=True, exist_ok=True)
        return tts_dir / f"{key}.mp3"

    def save_tts(self, source_path: Path, text: str, voice_config: dict) -> Path:
        """Copy a generated TTS file into the cache and return its path."""
        dest = self.get_tts_cache_path(text, voice_config)
        shutil.copy2(source_path, dest)
        return dest

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def clear(self, namespace: Optional[str] = None) -> None:
        """Remove cached entries (all, or a specific namespace)."""
        target = self.cache_dir / namespace if namespace else self.cache_dir
        if target.exists():
            shutil.rmtree(target)
            target.mkdir(parents=True, exist_ok=True)

    def stats(self) -> dict:
        """Return simple cache statistics."""
        counts: dict = {}
        for ns_dir in self.cache_dir.iterdir():
            if ns_dir.is_dir():
                counts[ns_dir.name] = len(list(ns_dir.iterdir()))
        return counts
