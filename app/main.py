"""
Main FastAPI application entry point.
Initializes the app, creates database tables, and sets up routes.
"""

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine
from app.db.models import Base
from app.api.api_v1.api import api_router
from app.services.scheduler import start_scheduler, stop_scheduler
import logging

logger = logging.getLogger(__name__)


# Create database tables on startup
def create_tables():
    """Create all database tables on application startup"""
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Create tables
    create_tables()
    print("✓ Database tables created/verified")
    
    # Start background scheduler for deadline alerts
    try:
        start_scheduler()
        print("✓ Background scheduler started")
    except Exception as e:
        logger.error(f"Failed to start scheduler: {e}")
    
    print(f"✓ Starting {settings.APP_NAME}")
    yield
    
    # Shutdown
    stop_scheduler()
    print(f"✓ Shutting down {settings.APP_NAME}")


# CORS middleware configuration
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    ),
]

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered legal operations platform for case management, document organization, and deadline tracking",
    version="1.0.0",
    docs_url="/api/v1/docs",
    middleware=middleware,
    lifespan=lifespan,
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running.
    
    Returns:
        dict: Status and message
    """
    return {
        "status": "healthy",
        "message": "API is running",
        "service": settings.APP_NAME
    }


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with API documentation link"""
    return {
        "message": "Welcome to AI Legal Operations Platform",
        "docs": "/api/v1/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
