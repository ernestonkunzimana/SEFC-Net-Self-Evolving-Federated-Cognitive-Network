"""
Rate Limiting Middleware for SEFCNet
===================================
"""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window"""
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_windows: dict[str, list[float]] = defaultdict(list)
        self.hour_windows: dict[str, list[float]] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Try to get user ID from token if authenticated
        if hasattr(request.state, 'user_id'):
            return f"user:{request.state.user_id}"
        
        # Fall back to IP address
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    def _clean_old_requests(self, window: list[float], window_seconds: int):
        """Remove requests outside the time window"""
        current_time = time.time()
        cutoff = current_time - window_seconds
        return [t for t in window if t > cutoff]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/health", "/metrics", "/ready", "/live", "/"]:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Check per-minute limit
        self.minute_windows[client_id] = self._clean_old_requests(
            self.minute_windows[client_id], 60
        )
        if len(self.minute_windows[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
            )
        
        # Check per-hour limit
        self.hour_windows[client_id] = self._clean_old_requests(
            self.hour_windows[client_id], 3600
        )
        if len(self.hour_windows[client_id]) >= self.requests_per_hour:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.requests_per_hour} requests per hour"
            )
        
        # Record request
        self.minute_windows[client_id].append(current_time)
        self.hour_windows[client_id].append(current_time)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - len(self.minute_windows[client_id])
        )
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - len(self.hour_windows[client_id])
        )
        
        return response

