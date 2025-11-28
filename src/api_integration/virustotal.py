"""VirusTotal API integration."""
from __future__ import annotations

import logging
from typing import Optional

try:
    import vt
except ImportError:
    vt = None

from ..config import config
from .cache_manager import CacheManager
from .rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class VirusTotalClient:
    """Client for VirusTotal API v3."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.vt_api_key
        self.enabled = config.get('api.virustotal.enabled', True) and self.api_key is not None
        self.cache = CacheManager(ttl_hours=config.get('api.virustotal.cache_duration_hours', 24))
        self.rate_limiter = RateLimiter(
            max_calls=config.get('api.virustotal.rate_limit_per_minute', 4),
            time_window=60
        )
        
        if not self.enabled:
            logger.warning("VirusTotal client disabled: API key not configured")
        elif vt is None:
            logger.error("VirusTotal client unavailable: vt-py not installed")
            self.enabled = False
            
    def lookup_hash(self, file_hash: str) -> Optional[dict]:
        """
        Look up a file hash in VirusTotal.
        
        Args:
            file_hash: SHA-256 hash of the file
            
        Returns:
            Dictionary with detection results or None if not found/error
        """
        if not self.enabled:
            return None
            
        # Check cache first
        cached = self.cache.get(file_hash)
        if cached is not None:
            logger.debug(f"Cache hit for hash: {file_hash[:16]}...")
            return cached
            
        try:
            # Apply rate limiting
            self.rate_limiter.acquire()
            
            # Query VirusTotal
            with vt.Client(self.api_key) as client:
                try:
                    file_obj = client.get_object(f"/files/{file_hash}")
                    result = self._parse_response(file_obj)
                    
                    # Cache the result
                    self.cache.set(file_hash, result)
                    return result
                    
                except vt.APIError as e:
                    if e.code == "NotFoundError":
                        # File not in VT database
                        logger.debug(f"Hash not found in VirusTotal: {file_hash[:16]}...")
                        result = {'found': False}
                        self.cache.set(file_hash, result)
                        return result
                    else:
                        logger.error(f"VirusTotal API error: {e}")
                        return None
                        
        except Exception as e:
            logger.error(f"Error querying VirusTotal: {e}")
            return None
            
    def _parse_response(self, file_obj) -> dict:
        """Parse VirusTotal API response."""
        stats = file_obj.last_analysis_stats
        
        return {
            'found': True,
            'malicious': stats.get('malicious', 0),
            'suspicious': stats.get('suspicious', 0),
            'harmless': stats.get('harmless', 0),
            'undetected': stats.get('undetected', 0),
            'total_engines': sum(stats.values()),
            'threat_names': self._get_threat_names(file_obj),
            'first_seen': str(file_obj.first_submission_date) if hasattr(file_obj, 'first_submission_date') else None,
            'reputation': file_obj.reputation if hasattr(file_obj, 'reputation') else 0,
        }
        
    def _get_threat_names(self, file_obj) -> list[str]:
        """Extract unique threat names from detection results."""
        threat_names = set()
        
        if hasattr(file_obj, 'last_analysis_results'):
            for engine, result in file_obj.last_analysis_results.items():
                if result.get('category') in ['malicious', 'suspicious']:
                    name = result.get('result')
                    if name:
                        threat_names.add(name)
                        
        return list(threat_names)[:10]  # Limit to top 10
        
    def is_malicious(self, file_hash: str, threshold: int = 3) -> bool:
        """
        Check if a file is considered malicious based on detections.
        
        Args:
            file_hash: SHA-256 hash of the file
            threshold: Minimum number of engines that must flag as malicious
            
        Returns:
            True if malicious detections >= threshold
        """
        result = self.lookup_hash(file_hash)
        
        if not result or not result.get('found'):
            return False
            
        malicious_count = result.get('malicious', 0) + result.get('suspicious', 0)
        return malicious_count >= threshold
