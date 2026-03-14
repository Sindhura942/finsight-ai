"""Expense service for business logic"""

import os
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.logger import app_logger
from app.models import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.database.repository import ExpenseRepository

# Optional imports with fallback
try:
    from .ocr_service import OCRService
except ImportError:
    OCRService = None

try:
    from .llm_service import LLMService
except ImportError:
    LLMService = None


class ExpenseService:
    """Service for expense management and processing"""

    def __init__(self, db: Session, ocr_service = None, llm_service = None):
        """Initialize expense service
        
        Args:
            db: Database session
            ocr_service: OCR service instance (optional)
            llm_service: LLM service instance (optional)
        """
        self.db = db
        self.repository = ExpenseRepository(db)
        self.ocr_service = ocr_service
        self.llm_service = llm_service
        self.logger = app_logger
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)

    def process_receipt_image(self, image_path: str) -> ExpenseResponse:
        """Process a receipt image and extract expense information
        
        Args:
            image_path: Path to receipt image
            
        Returns:
            Created ExpenseResponse
        """
        try:
            self.logger.info(f"Processing receipt image: {image_path}")
            
            # Extract text from image
            text, ocr_confidence = self.ocr_service.extract_text_from_image(image_path)
            self.logger.info(f"Extracted text with confidence {ocr_confidence:.2f}")
            
            # Extract expense details
            details = self.llm_service.extract_expense_details(text)
            
            merchant_name = details.get("merchant_name", "Unknown")
            amount = float(details.get("amount", 0.0))
            
            # Categorize expense
            category = self.llm_service.categorize_expense(merchant_name, text[:200])
            
            # Create expense record
            expense_create = ExpenseCreate(
                merchant_name=merchant_name,
                amount=amount,
                category=category,
                image_path=image_path,
                confidence_score=ocr_confidence,
                description=text[:500],
            )
            
            expense_orm = self.repository.create(expense_create)
            
            self.logger.info(f"Successfully processed receipt: {expense_orm.id}")
            
            return self._orm_to_response(expense_orm)
        
        except Exception as e:
            self.logger.error(f"Failed to process receipt: {str(e)}")
            raise

    def create_expense(self, expense: ExpenseCreate) -> ExpenseResponse:
        """Create a new expense
        
        Args:
            expense: Expense data
            
        Returns:
            Created ExpenseResponse
        """
        try:
            expense_orm = self.repository.create(expense)
            self.logger.info(f"Created expense: {expense_orm.id}")
            return self._orm_to_response(expense_orm)
        except Exception as e:
            self.logger.error(f"Failed to create expense: {str(e)}")
            raise

    def get_expense(self, expense_id: int) -> Optional[ExpenseResponse]:
        """Get expense by ID
        
        Args:
            expense_id: Expense ID
            
        Returns:
            ExpenseResponse or None
        """
        expense_orm = self.repository.get_by_id(expense_id)
        if expense_orm:
            return self._orm_to_response(expense_orm)
        return None

    def get_all_expenses(self, skip: int = 0, limit: int = 100) -> List[ExpenseResponse]:
        """Get all expenses with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of ExpenseResponse
        """
        expenses = self.repository.get_all(skip, limit)
        return [self._orm_to_response(e) for e in expenses]

    def update_expense(self, expense_id: int, expense_update: ExpenseUpdate) -> Optional[ExpenseResponse]:
        """Update an expense
        
        Args:
            expense_id: Expense ID
            expense_update: Updated expense data
            
        Returns:
            Updated ExpenseResponse or None
        """
        expense_orm = self.repository.update(expense_id, expense_update)
        if expense_orm:
            self.logger.info(f"Updated expense: {expense_id}")
            return self._orm_to_response(expense_orm)
        return None

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense
        
        Args:
            expense_id: Expense ID
            
        Returns:
            True if deleted, False if not found
        """
        success = self.repository.delete(expense_id)
        if success:
            self.logger.info(f"Deleted expense: {expense_id}")
        return success

    @staticmethod
    def _orm_to_response(expense_orm) -> ExpenseResponse:
        """Convert ORM model to response schema"""
        return ExpenseResponse(
            id=expense_orm.id,
            merchant_name=expense_orm.merchant_name,
            amount=expense_orm.amount,
            category=expense_orm.category,
            date=expense_orm.date,
            description=expense_orm.description,
            image_path=expense_orm.image_path,
            confidence_score=expense_orm.confidence_score,
            created_at=expense_orm.created_at,
            updated_at=expense_orm.updated_at,
        )
