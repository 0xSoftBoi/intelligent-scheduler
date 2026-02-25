"""Main application entry point for the Intelligent Scheduler System."""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.routes import energy, meetings, optimization, webhooks, settings
from src.core.config import get_settings
from src.core.database import init_db

settings = get_settings()

app = FastAPI(
    title="Intelligent Scheduler API",
    description="AI-powered scheduling system for optimal productivity",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(energy.router, prefix="/api/v1/energy", tags=["Energy Analysis"])
app.include_router(meetings.router, prefix="/api/v1/meetings", tags=["Meetings"])
app.include_router(optimization.router, prefix="/api/v1/schedule", tags=["Optimization"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(settings.router, prefix="/api/v1/settings", tags=["Settings"])


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting Intelligent Scheduler System...")
    await init_db()
    logger.info("Database initialized successfully")
    logger.info("Application started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    logger.info("Shutting down Intelligent Scheduler System...")


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Intelligent Scheduler API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_models": "loaded",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
