"""
Enterprise-grade caching system with Redis and in-memory fallback
"""
from typing import Any, Dict, Optional, Union, List
from datetime import datetime, timedelta
import json
import asyncio
from functools import wraps

import redis
from redis.cluster import RedisCluster
import aioredis
from cachetools import TTLCache, LRUCache
from fastapi import HTTPException

from ..utils.logger import get_logger

logger = get_logger(__name__)

class EnterpriseCache:
    """Enterprise-grade distributed caching system"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        fallback_size: int = 1000,
        default_ttl: int = 300,
        cluster_mode: bool = False
    ):
        """Initialize caching system"""
        self.default_ttl = default_ttl
        
        # Redis connection
        try:
            if cluster_mode:
                self.redis = RedisCluster.from_url(redis_url)
            else:
                self.redis = redis.from_url(redis_url)
            
            # Async Redis connection
            self.async_redis = aioredis.from_url(redis_url)
            
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}. Using in-memory cache.")
            self.redis = None
            self.async_redis = None
        
        # In-memory fallback caches
        self.ttl_cache = TTLCache(maxsize=fallback_size, ttl=default_ttl)
        self.lru_cache = LRUCache(maxsize=fallback_size)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Try Redis first
            if self.async_redis:
                value = await self.async_redis.get(key)
                if value:
                    return json.loads(value)
            
            # Fallback to in-memory cache
            return self.ttl_cache.get(key) or self.lru_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_lru: bool = False
    ) -> bool:
        """Set value in cache"""
        try:
            serialized = json.dumps(value)
            ttl = ttl or self.default_ttl
            
            # Try Redis first
            if self.async_redis:
                await self.async_redis.set(key, serialized, ex=ttl)
            
            # Also set in fallback cache
            if use_lru:
                self.lru_cache[key] = value
            else:
                self.ttl_cache[key] = value
            
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            # Delete from Redis
            if self.async_redis:
                await self.async_redis.delete(key)
            
            # Delete from fallback caches
            self.ttl_cache.pop(key, None)
            self.lru_cache.pop(key, None)
            
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
    
    async def clear(self) -> bool:
        """Clear all caches"""
        try:
            # Clear Redis
            if self.async_redis:
                await self.async_redis.flushdb()
            
            # Clear fallback caches
            self.ttl_cache.clear()
            self.lru_cache.clear()
            
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def cached(
        self,
        ttl: Optional[int] = None,
        use_lru: bool = False,
        key_prefix: str = ""
    ):
        """Cache decorator for async functions"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try to get from cache
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                await self.set(cache_key, result, ttl=ttl, use_lru=use_lru)
                
                return result
            return wrapper
        return decorator
    
    def invalidate_pattern(self, pattern: str) -> bool:
        """Invalidate all keys matching pattern"""
        try:
            if self.redis:
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
            
            # Also clear matching keys in fallback caches
            for cache in [self.ttl_cache, self.lru_cache]:
                keys_to_delete = [
                    k for k in cache.keys()
                    if k.startswith(pattern.replace("*", ""))
                ]
                for k in keys_to_delete:
                    cache.pop(k, None)
            
            return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {str(e)}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            stats = {
                "ttl_cache_size": len(self.ttl_cache),
                "lru_cache_size": len(self.lru_cache),
                "redis_connected": bool(self.redis)
            }
            
            if self.redis:
                info = self.redis.info()
                stats.update({
                    "redis_memory_used": info["used_memory_human"],
                    "redis_total_keys": info["db0"]["keys"],
                    "redis_hits": info["keyspace_hits"],
                    "redis_misses": info["keyspace_misses"]
                })
            
            return stats
        except Exception as e:
            logger.error(f"Cache stats error: {str(e)}")
            return {}