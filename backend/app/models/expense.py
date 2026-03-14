"""Expense data models and schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    """Request model for creating an expense"""

    merchant_name: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=100)
    date: datetime = Field(default_factory=datetime.now)
    description: Optional[str] = Field(None, max_length=500)
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
    """Request model for updating an expense"""

    merchant_name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "merchant_name": "Updated Merchant",
                "amount": 10.00,
                "category": "Food & Dining",
                "description": "Updated description",
            }
        }


class Expense(BaseModel):
    """Database model for expenses"""

    id: int
    merchant_name: str
    amount: float
    category: str
    date: datetime
    description: Optional[str]
    image_path: Optional[str]
    confidence_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpenseResponse(BaseModel):
    """Response model for expense endpoints"""

    id: int
    merchant_name: str
    amount: float
    category: str
    date: datetime
    description: Optional[str]
    image_path: Optional[str]
    confidence_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
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
