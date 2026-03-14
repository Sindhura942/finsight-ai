"""Insights and analytics data models"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CategoryInsight(BaseModel):
    """Insight for a spending category"""

    category: str
    total_amount: float
    transaction_count: int
    average_transaction: float
    percentage_of_total: float

    class Config:
        json_schema_extra = {
            "example": {
                "category": "Food & Dining",
                "total_amount": 150.50,
                "transaction_count": 10,
                "average_transaction": 15.05,
                "percentage_of_total": 25.5,
            }
        }


class SpendingSummary(BaseModel):
    """Overall spending summary"""

    total_spending: float
    transaction_count: int
    average_transaction: float
    highest_category: str
    period: str
    categories: List[CategoryInsight]

    class Config:
        json_schema_extra = {
            "example": {
                "total_spending": 590.00,
                "transaction_count": 25,
                "average_transaction": 23.60,
                "highest_category": "Food & Dining",
                "period": "March 2024",
                "categories": [],
            }
        }


class SpendingTrend(BaseModel):
    """Spending trend data point"""

    date: datetime
    amount: float
    category: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-03-13",
                "amount": 50.00,
                "category": "Food & Dining",
            }
        }


class CostSavingSuggestion(BaseModel):
    """AI-generated cost-saving suggestion"""

    title: str
    description: str
    potential_savings: float
    category: str
    priority: str = Field(..., pattern="^(high|medium|low)$")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Reduce dining frequency",
                "description": "You spent $150 on Food & Dining. Consider cooking at home 2-3 times more per week.",
                "potential_savings": 30.00,
                "category": "Food & Dining",
                "priority": "high",
            }
        }


class RecommendationsResponse(BaseModel):
    """Response with AI recommendations"""

    suggestions: List[CostSavingSuggestion]
    total_potential_savings: float
    analysis_period: str

    class Config:
        json_schema_extra = {
            "example": {
                "suggestions": [],
                "total_potential_savings": 100.00,
                "analysis_period": "Last 30 days",
            }
        }


class InsightRequest(BaseModel):
    """Request for insights analysis"""

    days: int = Field(default=30, ge=1, le=365)
    category: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "days": 30,
                "category": "Food & Dining",
            }
        }
