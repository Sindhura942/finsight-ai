"""
Data Transfer Objects for Expense management.

DTOs provide a clean separation between API contracts and internal models.
They define request/response schemas with validation.

Examples:
    Creating an expense:
        request = ExpenseCreate(
            merchant="Whole Foods",
            amount=45.50,
            category="Food",
            date="2024-03-13"
        )
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator


class ExpenseCategory(str, Enum):
    """Expense categories."""
    FOOD = "Food"
    TRANSPORT = "Transport"
    SHOPPING = "Shopping"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    HEALTH = "Health"
    OTHER = "Other"


class ExpenseCreate(BaseModel):
    """Schema for creating an expense."""
    
    merchant: str = Field(..., min_length=2, max_length=255, description="Merchant name")
    amount: float = Field(..., gt=0, description="Expense amount")
    category: ExpenseCategory = Field(..., description="Expense category")
    date: datetime = Field(default_factory=datetime.now, description="Expense date")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    receipt_image_url: Optional[str] = Field(None, description="Receipt image URL")
    
    @validator("merchant")
    def validate_merchant(cls, v):
        """Validate merchant name is not empty."""
        if not v or not v.strip():
            raise ValueError("Merchant name cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "merchant": "Whole Foods Market",
                "amount": 45.50,
                "category": "Food",
                "date": "2024-03-13T10:30:00",
                "description": "Weekly groceries"
            }
        }


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense."""
    
    merchant: Optional[str] = Field(None, min_length=2, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[ExpenseCategory] = None
    date: Optional[datetime] = None
    description: Optional[str] = Field(None, max_length=1000)


class ExpenseResponse(BaseModel):
    """Schema for expense response."""
    
    id: int
    merchant: str
    amount: float
    category: ExpenseCategory
    date: datetime
    description: Optional[str]
    receipt_image_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        """Pydantic config."""
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "merchant": "Whole Foods Market",
                "amount": 45.50,
                "category": "Food",
                "date": "2024-03-13T10:30:00",
                "description": "Weekly groceries",
                "receipt_image_url": None,
                "created_at": "2024-03-13T10:35:00",
                "updated_at": None
            }
        }


class ReceiptUploadRequest(BaseModel):
    """Schema for receipt upload request."""
    
    image_data: str = Field(..., description="Base64 encoded image data")
    filename: str = Field(..., description="Original filename")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "image_data": "iVBORw0KGgoAAAANS...",
                "filename": "receipt.jpg"
            }
        }


class ReceiptAnalysisResult(BaseModel):
    """Schema for receipt analysis result."""
    
    merchant: Optional[str] = Field(None, description="Extracted merchant name")
    amount: Optional[float] = Field(None, description="Extracted amount")
    date: Optional[datetime] = Field(None, description="Extracted date")
    category: Optional[ExpenseCategory] = Field(None, description="Suggested category")
    confidence: float = Field(..., ge=0, le=1, description="Overall confidence score")
    items: Optional[List[dict]] = Field(None, description="Extracted items")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "merchant": "Whole Foods Market",
                "amount": 45.50,
                "date": "2024-03-13",
                "category": "Food",
                "confidence": 0.92,
                "items": [
                    {"name": "Apples", "price": 3.99},
                    {"name": "Milk", "price": 4.50}
                ]
            }
        }


class SpendingSummaryResponse(BaseModel):
    """Schema for spending summary response."""
    
    total_spending: float = Field(..., description="Total spending amount")
    average_daily: float = Field(..., description="Average spending per day")
    transaction_count: int = Field(..., description="Number of transactions")
    by_category: dict = Field(..., description="Breakdown by category")
    period_days: int = Field(..., description="Number of days analyzed")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "total_spending": 500.00,
                "average_daily": 16.67,
                "transaction_count": 30,
                "by_category": {
                    "Food": 200.00,
                    "Transport": 150.00,
                    "Other": 150.00
                },
                "period_days": 30
            }
        }


class BudgetAlert(BaseModel):
    """Schema for budget alert."""
    
    category: ExpenseCategory
    current_spending: float
    budget_limit: float
    status: str = Field(..., description="Alert status: normal, near, over")
    percentage: float = Field(..., ge=0, le=200, description="Percentage of budget used")


class MonthlyInsights(BaseModel):
    """Schema for monthly insights."""
    
    month: str = Field(..., description="Month in YYYY-MM format")
    total_spending: float
    transaction_count: int
    average_transaction: float
    top_categories: List[dict] = Field(..., description="Top spending categories")
    month_over_month_change: float = Field(..., description="Percentage change from previous month")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "month": "2024-03",
                "total_spending": 1250.50,
                "transaction_count": 45,
                "average_transaction": 27.79,
                "top_categories": [
                    {"category": "Food", "amount": 437.68},
                    {"category": "Transport", "amount": 312.50}
                ],
                "month_over_month_change": 12.5
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error response."""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "Invalid expense amount",
                "details": {"field": "amount", "reason": "must be greater than 0"},
                "timestamp": "2024-03-13T10:35:00"
            }
        }
