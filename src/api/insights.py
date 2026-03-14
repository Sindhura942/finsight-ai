"""Insights API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.services import InsightService
from src.schemas import SpendingSummary, RecommendationsResponse
from src.utils import get_logger

logger = get_logger("insights_api")

router = APIRouter(
    prefix="/api/insights",
    tags=["insights"],
)


@router.get("/summary", response_model=SpendingSummary)
async def get_spending_summary(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Get spending summary"""
    try:
        if days < 1 or days > 365:
            raise ValueError("Days must be between 1 and 365")
        
        service = InsightService(db)
        return service.get_spending_summary(days)
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get summary: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recommendations", response_model=RecommendationsResponse)
async def get_recommendations(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Get cost-saving recommendations"""
    try:
        if days < 1 or days > 365:
            raise ValueError("Days must be between 1 and 365")
        
        service = InsightService(db)
        return service.get_recommendations(days)
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get recommendations: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trends")
async def get_spending_trends(
    days: int = 30,
    db: Session = Depends(get_db),
):
    """Get spending trends over time"""
    try:
        if days < 1 or days > 365:
            raise ValueError("Days must be between 1 and 365")
        
        service = InsightService(db)
        summary = service.get_spending_summary(days)
        
        return {
            "period": summary.period,
            "total": summary.total_spending,
            "trend": "increasing" if summary.transaction_count > 0 else "flat",
            "categories": [
                {
                    "name": cat.category,
                    "amount": cat.total_amount,
                    "percent": cat.percentage_of_total,
                }
                for cat in summary.categories
            ],
        }
    except ValueError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get trends: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
