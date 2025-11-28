"""Cache manager for API responses."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

from ..config import ROOT_PATH

CACHE_DIR = ROOT_PATH / "data" / "api_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class CacheManager:
    """Manages caching of API responses to reduce API calls."""
    
    def __init__(self, cache_dir: Path = CACHE_DIR, ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_hours * 3600
        
    def get(self, key: str) -> Optional[dict[str, Any]]:
        """Get cached value if it exists and is not expired."""
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check if expired
            if time.time() - data.get('timestamp', 0) > self.ttl_seconds:
                cache_file.unlink(missing_ok=True)
                return None
                
            return data.get('value')
        except (json.JSONDecodeError, IOError):
            return None
            
    def set(self, key: str, value: dict[str, Any]) -> None:
        """Cache a value with timestamp."""
        cache_file = self._get_cache_file(key)
        
        data = {
            'timestamp': time.time(),
            'value': value,
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except IOError:
            pass  # Silently fail if unable to cache
            
    def clear(self) -> None:
        """Clear all cached entries."""
        for cache_file in self.cache_dir.glob('*.json'):
            cache_file.unlink(missing_ok=True)
            
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for a key."""
        # Use hash of key as filename to avoid invalid characters
        filename = f"{hash(key) % 10**10}.json"
        return self.cache_dir / filename
