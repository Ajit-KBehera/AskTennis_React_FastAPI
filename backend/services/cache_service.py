from abc import ABC, abstractmethod
from typing import Any, Optional
import os
import diskcache

class CacheService(ABC):
    """Abstract base class for caching services."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, expire: int = 86400) -> None:
        """Set a value in the cache with an expiration time (default 24h)."""
        pass

class DiskCacheService(CacheService):
    """Disk-based caching implementation using diskcache."""
    
    def __init__(self, cache_dir: str = ".cache"):
        # Resolve absolute path for cache directory
        if not os.path.isabs(cache_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cache_dir = os.path.join(base_dir, cache_dir)
            
        self.cache = diskcache.Cache(cache_dir)
        print(f"--- Cache initialized at {cache_dir} ---")

    def get(self, key: str) -> Optional[Any]:
        return self.cache.get(key)

    def set(self, key: str, value: Any, expire: int = 86400) -> None:
        self.cache.set(key, value, expire=expire)

import redis
import json
import pickle

class RedisCacheService(CacheService):
    """Redis-based caching implementation."""
    
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        print(f"--- Redis Cache initialized at {redis_url} ---")

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis.get(key)
            if data:
                return pickle.loads(data)
        except Exception as e:
            print(f"Error reading from Redis: {e}")
        return None

    def set(self, key: str, value: Any, expire: int = 86400) -> None:
        try:
            pickled_value = pickle.dumps(value)
            self.redis.set(key, pickled_value, ex=expire)
        except Exception as e:
            print(f"Error writing to Redis: {e}")

class CacheFactory:
    """Factory to create the appropriate cache service."""
    
    @staticmethod
    def get_service() -> CacheService:
        """
        Returns a CacheService instance.
        Returns RedisCacheService if REDIS_URL is set, otherwise DiskCacheService.
        """
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            return RedisCacheService(redis_url)
        return DiskCacheService()
