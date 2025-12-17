"""FastAPI main application for FinAgent."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import sse

from app.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting FinAgent API...")
    yield
    # Shutdown
    logger.info("Shutting down FinAgent API...")


# Create FastAPI app
app = FastAPI(
    title="FinAgent API",
    description="Financial Agent powered by LLMs with React Agent pattern",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "FinAgent API",
        "version": "0.1.0",
        "description": "Financial Agent powered by LLMs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(sse.router, prefix="/sse", tags=["sse"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower(),
    )
