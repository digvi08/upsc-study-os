"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.routes import api_router
from app.middleware import LoggingMiddleware, SecurityHeadersMiddleware

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version} [{settings.environment}]")
    if settings.is_production:
        logger.info("Production mode: schema managed by Alembic (see start.sh)")
    else:
        init_db()
        logger.info("Database tables initialized")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered UPSC/MPSC Study Operating System API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.is_production:
    app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(LoggingMiddleware)
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint for health checks and quick API discovery."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else None,
        "health": "/health",
        "api": "/api/v1",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Render/Railway."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    detail = str(exc) if settings.debug else "Internal server error"
    return JSONResponse(
        status_code=500,
        content={"detail": detail, "error_code": "INTERNAL_ERROR"},
    )
