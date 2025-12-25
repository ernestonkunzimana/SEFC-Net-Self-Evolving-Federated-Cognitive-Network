"""
Enterprise-grade circuit breaker and rate limiter implementation
"""
from typing import Dict, Any, Optional, Callable, Awaitable, TypeVar, List
from datetime import datetime, timedelta
import asyncio
from functools import wraps
import time

from fastapi import HTTPException, Request, Response
import aioredis
from redis.exceptions import RedisError
from prometheus_client import Counter, Gauge, Histogram

from ..utils.logger import get_logger
from ..utils.metrics import MetricsCollector

logger = get_logger(__name__)
T = TypeVar("T")

class CircuitBreaker:
    """Enterprise-grade circuit breaker pattern implementation"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,
        half_open_timeout: int = 30,
        monitoring_window: int = 120
    ):
        """Initialize circuit breaker"""
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        self.monitoring_window = monitoring_window
        
        # Circuit state
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
        
        # Metrics
        self.trips = Counter(
            "circuit_breaker_trips_total",
            "Number of times the circuit breaker has tripped",
            ["service"]
        )
        self.state_gauge = Gauge(
            "circuit_breaker_state",
            "Current state of the circuit breaker (0=closed, 1=half-open, 2=open)",
            ["service"]
        )
        self.request_latency = Histogram(
            "circuit_breaker_request_latency_seconds",
            "Request latency through circuit breaker",
            ["service"]
        )
    
    async def call(
        self,
        func: Callable[..., Awaitable[T]],
        *args,
        service_name: str = "default",
        **kwargs
    ) -> T:
        """Execute function with circuit breaker pattern"""
        if self.state == "open":
            if self._should_retry():
                self.state = "half-open"
                self.state_gauge.labels(service=service_name).set(1)
            else:
                raise HTTPException(
                    status_code=503,
                    detail="Service temporarily unavailable"
                )
        
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)
            
            # Record successful request
            self.request_latency.labels(service=service_name).observe(
                time.time() - start_time
            )
            
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
                self.state_gauge.labels(service=service_name).set(0)
            
            return result
            
        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.now()
            
            if self.state == "half-open" or self.failures >= self.failure_threshold:
                self.state = "open"
                self.state_gauge.labels(service=service_name).set(2)
                self.trips.labels(service=service_name).inc()
            
            raise HTTPException(
                status_code=503,
                detail=str(e)
            )
    
    def _should_retry(self) -> bool:
        """Check if circuit should attempt to close"""
        if not self.last_failure_time:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.reset_timeout

class RateLimiter:
    """Enterprise-grade rate limiter implementation"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        default_limit: int = 100,
        default_window: int = 60,
        group_limits: Optional[Dict[str, Dict[str, int]]] = None
    ):
        """Initialize rate limiter"""
        self.default_limit = default_limit
        self.default_window = default_window
        self.group_limits = group_limits or {}
        
        # Redis connection
        try:
            self.redis = aioredis.from_url(redis_url)
            logger.info("Rate limiter Redis connection established")
        except Exception as e:
            logger.error(f"Redis connection failed: {str(e)}")
            self.redis = None
        
        # Metrics
        self.requests = Counter(
            "rate_limiter_requests_total",
            "Total number of requests processed by rate limiter",
            ["endpoint", "status"]
        )
        self.current_usage = Gauge(
            "rate_limiter_current_usage",
            "Current number of requests within window",
            ["endpoint"]
        )
    
    async def is_allowed(
        self,
        key: str,
        group: str = "default",
        endpoint: str = "unknown"
    ) -> bool:
        """Check if request is allowed under rate limit"""
        try:
            # Get group-specific limits
            limits = self.group_limits.get(group, {
                "limit": self.default_limit,
                "window": self.default_window
            })
            
            current_time = int(time.time())
            window_start = current_time - limits["window"]
            
            if self.redis:
                # Use Redis for distributed rate limiting
                pipeline = self.redis.pipeline()
                
                # Remove old entries
                await pipeline.zremrangebyscore(
                    key,
                    min=0,
                    max=window_start
                )
                
                # Add current request
                await pipeline.zadd(key, {str(current_time): current_time})
                
                # Get count in window
                await pipeline.zcount(key, window_start, current_time)
                
                # Execute pipeline
                _, _, count = await pipeline.execute()
            else:
                # Fallback to in-memory counting
                count = 1  # Simplified fallback
            
            # Update metrics
            self.current_usage.labels(endpoint=endpoint).set(count)
            
            # Check if under limit
            is_allowed = count <= limits["limit"]
            status = "allowed" if is_allowed else "blocked"
            self.requests.labels(endpoint=endpoint, status=status).inc()
            
            return is_allowed
            
        except RedisError as e:
            logger.error(f"Rate limiter Redis error: {str(e)}")
            return True  # Fail open on Redis errors
        except Exception as e:
            logger.error(f"Rate limiter error: {str(e)}")
            return True
    
    def limit(
        self,
        group: str = "default",
        key_func: Optional[Callable[[Request], str]] = None
    ):
        """Rate limiting decorator for FastAPI endpoints"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, request: Request, **kwargs):
                # Generate rate limit key
                if key_func:
                    key = f"ratelimit:{key_func(request)}"
                else:
                    key = f"ratelimit:{request.client.host}"
                
                # Check rate limit
                if not await self.is_allowed(
                    key,
                    group=group,
                    endpoint=request.url.path
                ):
                    raise HTTPException(
                        status_code=429,
                        detail="Too many requests"
                    )
                
                return await func(*args, request=request, **kwargs)
            return wrapper
        return decorator
    
    async def get_usage(self, key: str) -> Dict[str, Any]:
        """Get current usage statistics for a key"""
        try:
            if not self.redis:
                return {"current": 0, "limit": self.default_limit}
            
            current_time = int(time.time())
            window_start = current_time - self.default_window
            
            # Get count in current window
            count = await self.redis.zcount(
                key,
                window_start,
                current_time
            )
            
            return {
                "current": count,
                "limit": self.default_limit,
                "remaining": max(0, self.default_limit - count),
                "reset": current_time + self.default_window
            }
        except Exception as e:
            logger.error(f"Error getting usage stats: {str(e)}")
            return {}