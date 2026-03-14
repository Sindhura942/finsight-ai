"""FastAPI application entry point for FinSight AI"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings
from src.database import init_db
from src.api import expenses_router, insights_router, health_router
from src.utils import get_logger

# Initialize logger
logger = get_logger("main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting FinSight AI")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FinSight AI")


# Create FastAPI app
app = FastAPI(
    title="FinSight AI",
    description="Intelligent financial expense tracking and cost-saving recommendations",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(expenses_router)
app.include_router(insights_router)
app.include_router(health_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to FinSight AI",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/")
async def api_root():
    """API root endpoint"""
    return {
        "api": "FinSight AI",
        "version": "0.1.0",
        "endpoints": {
            "expenses": "/api/expenses",
            "insights": "/api/insights",
            "health": "/api/health",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL,
    )
