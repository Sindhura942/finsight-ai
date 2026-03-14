"""Health check endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.agents import LLMAgent
from src.utils import get_logger

logger = get_logger("health_api")

router = APIRouter(
    prefix="/api/health",
    tags=["health"],
)


@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "FinSight AI",
        "version": "0.1.0",
    }


@router.get("/database")
async def database_health(
    db: Session = Depends(get_db),
):
    """Check database health"""
    try:
        # Execute a simple query
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "component": "database",
            "message": "Database connection OK",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "component": "database",
            "error": str(e),
        }


@router.get("/llm")
async def llm_health():
    """Check LLM service health"""
    try:
        llm = LLMAgent()
        is_healthy = llm.health_check()
        
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "component": "llm",
            "message": "LLM service OK" if is_healthy else "LLM service unavailable",
        }
    except Exception as e:
        logger.error(f"LLM health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "component": "llm",
            "error": str(e),
        }


@router.get("/status")
async def full_status(
    db: Session = Depends(get_db),
):
    """Get full system status"""
    db_health = "healthy"
    try:
        db.execute("SELECT 1")
    except Exception as e:
        db_health = "unhealthy"
        logger.error(f"Database check failed: {str(e)}")
    
    llm_health = "healthy"
    try:
        llm = LLMAgent()
        if not llm.health_check():
            llm_health = "unhealthy"
    except Exception as e:
        llm_health = "unhealthy"
        logger.error(f"LLM check failed: {str(e)}")
    
    overall_status = "healthy" if db_health == "healthy" and llm_health == "healthy" else "degraded"
    
    return {
        "overall": overall_status,
        "components": {
            "database": db_health,
            "llm": llm_health,
        },
        "service": "FinSight AI",
        "version": "0.1.0",
    }
