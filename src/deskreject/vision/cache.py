import hashlib
import json
from pathlib import Path


class VisionCache:
    """Cache for vision results, keyed by image content, prompt, and schema."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir / "vision"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_key(self, image_png: bytes, prompt: str, schema: dict) -> str:
        """Compute the cache key (excludes endpoint)."""
        hasher = hashlib.sha256()
        hasher.update(image_png)
        hasher.update(prompt.encode("utf-8"))
        # Canonical schema JSON
        hasher.update(json.dumps(schema, sort_keys=True).encode("utf-8"))
        return hasher.hexdigest()

    def get(self, image_png: bytes, prompt: str, schema: dict) -> dict | None:
        """Retrieve cached result if it exists."""
        key = self._get_key(image_png, prompt, schema)
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None
        return None

    def set(self, image_png: bytes, prompt: str, schema: dict, result: dict) -> None:
        """Store result in cache."""
        key = self._get_key(image_png, prompt, schema)
        path = self.cache_dir / f"{key}.json"
        path.write_text(json.dumps(result), encoding="utf-8")
