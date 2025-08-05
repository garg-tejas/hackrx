import threading
import time
from typing import List, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class APIKeyRotator:
    """Service to rotate between multiple API keys."""
    
    def __init__(self):
        self.keys = self._get_available_keys()
        self.current_index = 0
        self.lock = threading.Lock()
        self.last_used = {}  # Track last usage time for each key
        self.rate_limit_windows = {}  # Track rate limit windows
        
        logger.info(f"Initialized API key rotator with {len(self.keys)} keys")
    
    def _get_available_keys(self) -> List[str]:
        """Get all available API keys."""
        keys = []
        
        # Add primary key
        if settings.GOOGLE_API_KEY:
            keys.append(settings.GOOGLE_API_KEY)
        
        # Add secondary key if set
        if settings.GOOGLE_API_KEY_2:
            keys.append(settings.GOOGLE_API_KEY_2)
        
        if not keys:
            raise ValueError("No Google API keys found. Please set GOOGLE_API_KEY.")
        
        return keys
    
    def get_next_key(self) -> str:
        """Get the next available API key using round-robin rotation."""
        with self.lock:
            if not self.keys:
                raise ValueError("No API keys available")
            
            # Get current key
            key = self.keys[self.current_index]
            
            # Move to next key
            self.current_index = (self.current_index + 1) % len(self.keys)
            
            # Update last used time
            self.last_used[key] = time.time()
            
            logger.debug(f"Using API key {self.current_index + 1} of {len(self.keys)}")
            return key
    
    def get_available_key(self) -> Optional[str]:
        """Get an available key that's not rate limited."""
        with self.lock:
            current_time = time.time()
            
            for i, key in enumerate(self.keys):
                # Check if key was used recently (rate limit protection)
                last_used = self.last_used.get(key, 0)
                if current_time - last_used >= 6:  # 6 seconds between uses per key (10 RPM limit)
                    self.last_used[key] = current_time
                    logger.debug(f"Using API key {i + 1} of {len(self.keys)}")
                    return key
            
            # If all keys are rate limited, wait and return the least recently used
            if self.keys:
                least_recent_key = min(self.keys, key=lambda k: self.last_used.get(k, 0))
                self.last_used[least_recent_key] = current_time
                logger.warning("All keys rate limited, using least recently used key")
                return least_recent_key
            
            return None
    
    def mark_key_rate_limited(self, key: str):
        """Mark a key as rate limited."""
        with self.lock:
            self.rate_limit_windows[key] = time.time()
            logger.warning(f"API key marked as rate limited: {key[:10]}...")
    
    def get_key_status(self) -> dict:
        """Get status of all API keys."""
        current_time = time.time()
        status = {
            "total_keys": len(self.keys),
            "current_index": self.current_index,
            "keys": []
        }
        
        for i, key in enumerate(self.keys):
            last_used = self.last_used.get(key, 0)
            time_since_last_use = current_time - last_used
            is_rate_limited = time_since_last_use < 6
            
            status["keys"].append({
                "index": i + 1,
                "last_used": last_used,
                "time_since_last_use": time_since_last_use,
                "is_rate_limited": is_rate_limited,
                "key_preview": f"{key[:10]}..."
            })
        
        return status 