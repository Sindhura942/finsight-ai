"""Insights API endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.insight_service import InsightService
from app.core.logger import app_logger

router = APIRouter()


@router.get("/spending-summary", summary="Get spending summary")
async def get_spending_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get spending summary for the specified period
    
    - **days**: Number of days to analyze (1-365)
    
    Returns:
        SpendingSummary with total spending and breakdown by category
    """
    try:
        insight_service = InsightService(db)
        summary = insight_service.get_spending_summary(days)
        
        # Return flat data - Streamlit will wrap it in {'success': True, 'data': ...}
        return {
            "summary": {
                "total_spending": summary.total_spending,
                "average_daily_spending": summary.average_transaction,
                "transaction_count": summary.transaction_count,
                "highest_category": summary.highest_category,
                "period": summary.period,
            },
            "by_category": [
                {
                    "category": cat.category,
                    "amount": cat.total_amount,
                    "count": cat.transaction_count,
                    "percentage": cat.percentage_of_total
                }
                for cat in summary.categories
            ],
            "insights": []
        }
    except Exception as e:
        app_logger.error(f"Failed to get spending summary: {str(e)}")
        raise


@router.get("/by-category", summary="Get spending by category")
async def get_spending_by_category(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get detailed spending breakdown by category
    
    - **days**: Number of days to analyze (1-365)
    
    Returns:
        List of CategoryInsight objects
    """
    try:
        insight_service = InsightService(db)
        return insight_service.get_spending_by_category(days)
    except Exception as e:
        app_logger.error(f"Failed to get spending by category: {str(e)}")
        raise


@router.get("/trends", summary="Get spending trends")
async def get_spending_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get spending trends over time
    
    - **days**: Number of days to analyze (1-365)
    
    Returns:
        List of SpendingTrend objects with daily spending amounts
    """
    try:
        insight_service = InsightService(db)
        return insight_service.get_spending_trends(days)
    except Exception as e:
        app_logger.error(f"Failed to get spending trends: {str(e)}")
        raise


@router.post("/recommendations", summary="Get cost-saving recommendations")
async def get_recommendations(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get cost-saving recommendations
    
    - **days**: Number of days of spending to analyze
    
    Returns:
        Dictionary with recommendations and savings estimate
    """
    try:
        insight_service = InsightService(db)
        return insight_service.get_recommendations(days)
    except Exception as e:
        app_logger.error(f"Failed to generate recommendations: {str(e)}")
        raise
