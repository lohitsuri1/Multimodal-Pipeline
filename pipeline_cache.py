"""Disk-based cache for pipeline outputs.

Cache key: SHA-256 of (inputs + preset name + tier) serialised as JSON.
Cached items are stored as JSON files under Config.CACHE_DIR / <subdir>/.

Usage
-----
    from pipeline_cache import get_cached, set_cached, make_cache_key

    key = make_cache_key(theme="...", preset="devotional", tier="free")
    cached = get_cached(key, "scripts")
    if cached is None:
        cached = expensive_call(...)
        set_cached(key, cached, "scripts")
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

from config import Config


# ---------------------------------------------------------------------------
# Cache key
# ---------------------------------------------------------------------------

def make_cache_key(**kwargs: Any) -> str:
    """
    Build a stable cache key from arbitrary keyword arguments.

    Keys are sorted before hashing so argument order does not matter.
    """
    serialised = json.dumps(kwargs, sort_keys=True, default=str)
    return hashlib.sha256(serialised.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Read / write
# ---------------------------------------------------------------------------

def _cache_path(key: str, subdir: str) -> Path:
    cache_dir = Config.CACHE_DIR / subdir
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{key}.json"


def get_cached(key: str, subdir: str) -> Optional[Any]:
    """
    Return the cached value for *key* in *subdir*, or ``None`` if not found.

    Parameters
    ----------
    key:    Cache key produced by :func:`make_cache_key`.
    subdir: Sub-directory name, e.g. ``"scripts"``, ``"titles"``, ``"shorts"``.
    """
    path = _cache_path(key, subdir)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            envelope = json.load(fh)
        return envelope.get("value")
    except (json.JSONDecodeError, OSError):
        return None


def set_cached(key: str, value: Any, subdir: str) -> None:
    """
    Persist *value* under *key* in *subdir*.

    Parameters
    ----------
    key:    Cache key produced by :func:`make_cache_key`.
    value:  Any JSON-serialisable value.
    subdir: Sub-directory name, e.g. ``"scripts"``, ``"titles"``, ``"shorts"``.
    """
    path = _cache_path(key, subdir)
    envelope = {"key": key, "subdir": subdir, "ts": time.time(), "value": value}
    with path.open("w", encoding="utf-8") as fh:
        json.dump(envelope, fh, indent=2, default=str)


def get_cached_audio_path(key: str) -> Optional[Path]:
    """
    Return the path to a cached TTS audio file, or ``None`` if not cached.

    Audio files are stored as ``<key>.mp3`` inside ``CACHE_DIR/tts/``.
    """
    audio_path = Config.CACHE_DIR / "tts" / f"{key}.mp3"
    return audio_path if audio_path.exists() else None


def cache_audio_path(key: str) -> Path:
    """
    Return the path where a TTS audio file should be saved for *key*.

    Creates the parent directory if necessary.
    """
    audio_dir = Config.CACHE_DIR / "tts"
    audio_dir.mkdir(parents=True, exist_ok=True)
    return audio_dir / f"{key}.mp3"
