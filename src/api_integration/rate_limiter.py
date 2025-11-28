"""Rate limiter for API calls."""
from __future__ import annotations

import time
from collections import deque
from threading import Lock


class RateLimiter:
    """Simple rate limiter using sliding window algorithm."""
    
    def __init__(self, max_calls: int, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in the time window
            time_window: Time window in seconds (default: 60 seconds)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: deque[float] = deque()
        self.lock = Lock()
        
    def acquire(self) -> None:
        """Block until a call is allowed under the rate limit."""
        with self.lock:
            now = time.time()
            
            # Remove calls outside the time window
            while self.calls and self.calls[0] < now - self.time_window:
                self.calls.popleft()
                
            # If we've hit the limit, wait
            if len(self.calls) >= self.max_calls:
                sleep_time = self.calls[0] + self.time_window - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Clean up old calls after sleeping
                    now = time.time()
                    while self.calls and self.calls[0] < now - self.time_window:
                        self.calls.popleft()
                        
            # Record this call
            self.calls.append(time.time())
            
    def reset(self) -> None:
        """Reset the rate limiter."""
        with self.lock:
            self.calls.clear()
