"""Expense service for managing expenses"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.database.repository import ExpenseRepository
from src.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from src.utils import get_logger

logger = get_logger("ExpenseService")


class ExpenseService:
    """Service for expense management"""

    def __init__(self, db: Session):
        """Initialize expense service
        
        Args:
            db: Database session
        """
        self.db = db
        self.repository = ExpenseRepository(db)

    def create(self, expense: ExpenseCreate) -> ExpenseResponse:
        """Create expense
        
        Args:
            expense: Expense data
            
        Returns:
            Created expense response
        """
        try:
            db_expense = self.repository.create(expense)
            logger.info(f"Created expense: {db_expense.id}")
            return self._to_response(db_expense)
        except Exception as e:
            logger.error(f"Failed to create expense: {str(e)}")
            raise

    def get(self, expense_id: int) -> Optional[ExpenseResponse]:
        """Get expense by ID
        
        Args:
            expense_id: Expense ID
            
        Returns:
            Expense response or None
        """
        db_expense = self.repository.get_by_id(expense_id)
        return self._to_response(db_expense) if db_expense else None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ExpenseResponse]:
        """Get all expenses
        
        Args:
            skip: Number to skip
            limit: Maximum to return
            
        Returns:
            List of expenses
        """
        expenses = self.repository.get_all(skip, limit)
        return [self._to_response(e) for e in expenses]

    def update(self, expense_id: int, expense_update: ExpenseUpdate) -> Optional[ExpenseResponse]:
        """Update expense
        
        Args:
            expense_id: Expense ID
            expense_update: Updated data
            
        Returns:
            Updated expense or None
        """
        try:
            db_expense = self.repository.update(expense_id, expense_update)
            if db_expense:
                logger.info(f"Updated expense: {expense_id}")
                return self._to_response(db_expense)
            return None
        except Exception as e:
            logger.error(f"Failed to update expense: {str(e)}")
            raise

    def delete(self, expense_id: int) -> bool:
        """Delete expense
        
        Args:
            expense_id: Expense ID
            
        Returns:
            True if deleted
        """
        try:
            success = self.repository.delete(expense_id)
            if success:
                logger.info(f"Deleted expense: {expense_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete expense: {str(e)}")
            raise

    @staticmethod
    def _to_response(db_expense):
        """Convert ORM to response schema"""
        return ExpenseResponse(
            id=db_expense.id,
            merchant_name=db_expense.merchant_name,
            amount=db_expense.amount,
            category=db_expense.category,
            date=db_expense.date,
            description=db_expense.description,
            image_path=db_expense.image_path,
            confidence_score=db_expense.confidence_score,
            created_at=db_expense.created_at,
            updated_at=db_expense.updated_at,
        )
