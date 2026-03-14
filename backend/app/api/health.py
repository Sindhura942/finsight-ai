"""Health check endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.llm_service import LLMService

router = APIRouter()


@router.get("/", summary="Health check")
async def health_check(db: Session = Depends(get_db)):
    """Check API and dependencies health status"""
    
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "ok"
    except:
        db_status = "error"
    
    # Check Ollama/LLM service
    llm_service = LLMService()
    llm_status = "ok" if llm_service.health_check() else "error"
    
    return {
        "status": "ok" if db_status == "ok" and llm_status == "ok" else "degraded",
        "database": db_status,
        "llm_service": llm_status,
    }
