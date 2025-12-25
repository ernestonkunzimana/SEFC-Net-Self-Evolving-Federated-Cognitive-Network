"""
SEFCNet - Main FastAPI Application
==================================
Enterprise-grade Self-Evolving Federated Computing Network
Complete REST API with all integrated services
"""

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Callable

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import uvicorn

# Import all routers
from auth.routes import router as auth_router
from core.routes import router as core_router
from analytics.routes import router as analytics_router
from monitoring.routes import router as monitoring_router
from orchestration.routes import router as orchestration_router
from dashboard.routes import router as dashboard_router

# Import database initialization
from auth.database import init_db, close_db

# MANDATORY: Import mandatory core system
from mandatory_core import get_mandatory_core

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'sefcnet_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'sefcnet_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# Application metadata
APP_NAME = "SEFCNet"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
SEFCNet - Enterprise-Grade Self-Evolving Federated Computing Network

A comprehensive federated learning platform with:
- 🔐 Authentication & Authorization (JWT, RBAC)
- 🧠 Federated Learning Orchestration
- 📊 Advanced Analytics & Monitoring
- 📈 Real-time Dashboards
- 🔄 Self-Evolution Capabilities
- 🚀 Production-Ready Deployment
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - handles startup and shutdown"""
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info("=" * 60)
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("✓ Database initialized")
        
        # Initialize system components
        logger.info("Initializing system components...")
        try:
            from core.system_manager import SystemManager
            config_path = Path(__file__).parent / "config" / "evolution_config.yaml"
            if config_path.exists():
                system_manager = SystemManager(str(config_path))
                system_manager.initialize()
                app.state.system_manager = system_manager
                logger.info("✓ System manager initialized")
        except Exception as e:
            logger.warning(f"System manager initialization skipped: {e}")
        
        # MANDATORY: Initialize mandatory core (ALL innovation components)
        logger.info("Initializing MANDATORY innovation components...")
        try:
            mandatory_core = get_mandatory_core()
            app.state.mandatory_core = mandatory_core
            logger.info("✓ MANDATORY core initialized (Quantum-RIS + Cognitive + Biological)")
            logger.info("  ALL components are MANDATORY - no optional features")
        except Exception as e:
            logger.error(f"MANDATORY core initialization FAILED: {e}", exc_info=True)
            raise  # Fail if mandatory components can't initialize
        
        logger.info("=" * 60)
        logger.info(f"{APP_NAME} is ready!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    try:
        await close_db()
        if hasattr(app.state, 'system_manager'):
            app.state.system_manager.cleanup()
        logger.info("✓ Cleanup complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests"""
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests"""
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        request_id = getattr(request.state, 'request_id', 'unknown')
        
        logger.info(f"Request: {request.method} {request.url.path} [ID: {request_id}]")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Update metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(process_time)
            
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.3f}s [ID: {request_id}]"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} "
                f"Error: {str(e)} Time: {process_time:.3f}s [ID: {request_id}]",
                exc_info=True
            )
            raise

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

# Rate Limiting Middleware (optional, can be enabled via env)
if os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true":
    from middleware.rate_limit import RateLimitMiddleware
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        requests_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    )

# Add middleware in order (last added = first executed)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware (if configured)
trusted_hosts = os.getenv("TRUSTED_HOSTS", "").split(",")
if trusted_hosts and trusted_hosts[0]:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=trusted_hosts
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions globally"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An error occurred"
        }
    )


# Health check endpoint (no auth required)
@app.get("/", tags=["health"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": time.time()
    }
    
    # Check database connection
    try:
        from auth.database import get_db
        db = await get_db()
        await db.connect()
        health_status["database"] = "connected"
        await db.close()
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check system manager
    if hasattr(app.state, 'system_manager'):
        health_status["system_manager"] = "initialized"
    else:
        health_status["system_manager"] = "not_initialized"
    
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/metrics", tags=["monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/ready", tags=["health"])
async def readiness_check():
    """Readiness check endpoint for Kubernetes"""
    try:
        from auth.database import get_db
        db = await get_db()
        await db.connect()
        await db.close()
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            content={"status": "not_ready", "error": str(e)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@app.get("/live", tags=["health"])
async def liveness_check():
    """Liveness check endpoint for Kubernetes"""
    return {"status": "alive"}


# Register all routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(core_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(monitoring_router, prefix="/api/v1")
app.include_router(orchestration_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

