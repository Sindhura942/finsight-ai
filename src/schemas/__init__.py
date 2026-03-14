"""Data schemas and models for API validation"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# ==================== Expense Schemas ====================

class ExpenseBase(BaseModel):
    """Base expense model"""
    merchant_name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    date: datetime = Field(default_factory=datetime.utcnow)
    description: Optional[str] = Field(None, max_length=500)


class ExpenseCreate(ExpenseBase):
    """Schema for creating expense"""
    image_path: Optional[str] = None
    confidence_score: float = Field(default=1.0, ge=0, le=1)

    class Config:
        json_schema_extra = {
            "example": {
                "merchant_name": "Starbucks",
                "amount": 5.50,
                "category": "Food & Dining",
                "date": "2024-03-13T10:30:00",
                "description": "Coffee and breakfast",
                "confidence_score": 0.95,
            }
        }


class ExpenseUpdate(BaseModel):
    """Schema for updating expense"""
    merchant_name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ExpenseResponse(ExpenseBase):
    """Schema for expense response"""
    id: int
    image_path: Optional[str]
    confidence_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "merchant_name": "Starbucks",
                "amount": 5.50,
                "category": "Food & Dining",
                "date": "2024-03-13T10:30:00",
                "description": "Coffee and breakfast",
                "image_path": "/uploads/receipt_123.jpg",
                "confidence_score": 0.95,
                "created_at": "2024-03-13T10:35:00",
                "updated_at": "2024-03-13T10:35:00",
            }
        }


# ==================== Insights Schemas ====================

class CategoryInsight(BaseModel):
    """Spending insight for a category"""
    category: str
    total_amount: float
    transaction_count: int
    average_transaction: float
    percentage_of_total: float


class SpendingSummary(BaseModel):
    """Overall spending summary"""
    total_spending: float
    transaction_count: int
    average_transaction: float
    highest_category: str
    period: str
    categories: List[CategoryInsight]


class SpendingTrend(BaseModel):
    """Spending trend data point"""
    date: datetime
    amount: float
    category: Optional[str] = None


class CostSavingSuggestion(BaseModel):
    """AI-generated cost-saving suggestion"""
    title: str
    description: str
    potential_savings: float
    category: str
    priority: str = Field(..., pattern="^(high|medium|low)$")


class RecommendationsResponse(BaseModel):
    """Response with AI recommendations"""
    suggestions: List[CostSavingSuggestion]
    total_potential_savings: float
    analysis_period: str


# ==================== Receipt Processing Schemas ====================

class ReceiptData(BaseModel):
    """Extracted receipt data"""
    merchant_name: str
    amount: float
    date: Optional[datetime] = None
    items: Optional[List[str]] = None


class ReceiptProcessingResult(BaseModel):
    """Result of receipt processing"""
    success: bool
    data: Optional[ReceiptData] = None
    confidence: float = Field(..., ge=0, le=1)
    error: Optional[str] = None


# ==================== API Response Schemas ====================

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    status_code: int


class SuccessResponse(BaseModel):
    """Success response schema"""
    message: str
    data: Optional[dict] = None
