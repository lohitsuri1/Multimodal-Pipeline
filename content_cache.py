"""File-based cache for generated content keyed by stable SHA-256 hash."""
import hashlib
import json
import time
from pathlib import Path
from typing import Any, Optional

from config import Config


class ContentCache:
    """
    File-based cache for scripts, titles, and TTS outputs.

    Keys are derived from a stable SHA-256 hash of the input data so that
    identical inputs always resolve to the same cached result.
    """

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = Path(cache_dir or Config.CACHE_DIR)
        self.enabled = Config.ENABLE_CACHE
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────

    def get(self, key_data: Any) -> Optional[Any]:
        """
        Retrieve cached content.

        Args:
            key_data: Hashable data used as the cache key (dict, str, list …).

        Returns:
            Cached content, or None if not found / cache is disabled.
        """
        if not self.enabled:
            return None

        cache_file = self._cache_file(key_data)
        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as fh:
                entry = json.load(fh)
            return entry.get("content")
        except Exception:
            return None

    def set(self, key_data: Any, content: Any) -> None:
        """
        Store content in the cache.

        Args:
            key_data: Data used as the cache key.
            content: JSON-serialisable content to cache.
        """
        if not self.enabled:
            return

        cache_file = self._cache_file(key_data)
        try:
            entry = {"content": content, "cached_at": time.time()}
            with open(cache_file, "w", encoding="utf-8") as fh:
                json.dump(entry, fh)
        except Exception as exc:
            print(f"Warning: Could not write to cache: {exc}")

    def clear(self) -> int:
        """Clear all cached entries.

        Returns:
            Number of entries removed.
        """
        if not self.cache_dir.exists():
            return 0

        count = 0
        for path in self.cache_dir.glob("*.json"):
            path.unlink()
            count += 1
        return count

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────

    def _key_hash(self, data: Any) -> str:
        """Return a stable SHA-256 hex digest for *data*."""
        serialised = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialised.encode()).hexdigest()

    def _cache_file(self, key_data: Any) -> Path:
        return self.cache_dir / f"{self._key_hash(key_data)}.json"
