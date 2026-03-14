"""FinSight AI FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logger import app_logger
from app.database.session import engine
from app.database.models import Base
from app.api import router as api_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Include API routes
app.include_router(api_router)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs",
        "redoc": "/redoc",
    }


# Exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    app_logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Handle startup events"""
    app_logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    app_logger.info(f"API running on {settings.api_host}:{settings.api_port}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Handle shutdown events"""
    app_logger.info(f"Shutting down {settings.api_title}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower(),
    )
