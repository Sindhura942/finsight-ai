"""Data access layer using repository pattern"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.schemas import ExpenseCreate, ExpenseUpdate
from .models import Expense


class ExpenseRepository:
    """Repository for expense database operations"""

    def __init__(self, db: Session):
        """Initialize repository
        
        Args:
            db: Database session
        """
        self.db = db

    def create(self, expense: ExpenseCreate) -> Expense:
        """Create new expense
        
        Args:
            expense: Expense data to create
            
        Returns:
            Created expense object
        """
        db_expense = Expense(**expense.model_dump())
        self.db.add(db_expense)
        self.db.commit()
        self.db.refresh(db_expense)
        return db_expense

    def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """Get expense by ID
        
        Args:
            expense_id: Expense ID
            
        Returns:
            Expense or None
        """
        return self.db.query(Expense).filter(Expense.id == expense_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Expense]:
        """Get all expenses with pagination
        
        Args:
            skip: Number to skip
            limit: Maximum to return
            
        Returns:
            List of expenses
        """
        return self.db.query(Expense).offset(skip).limit(limit).all()

    def update(self, expense_id: int, expense_update: ExpenseUpdate) -> Optional[Expense]:
        """Update expense
        
        Args:
            expense_id: Expense ID
            expense_update: Updated data
            
        Returns:
            Updated expense or None
        """
        db_expense = self.get_by_id(expense_id)
        if not db_expense:
            return None

        update_data = expense_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_expense, key, value)

        db_expense.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_expense)
        return db_expense

    def delete(self, expense_id: int) -> bool:
        """Delete expense
        
        Args:
            expense_id: Expense ID
            
        Returns:
            True if deleted, False if not found
        """
        db_expense = self.get_by_id(expense_id)
        if not db_expense:
            return False

        self.db.delete(db_expense)
        self.db.commit()
        return True

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Expense]:
        """Get expenses in date range
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of expenses
        """
        return self.db.query(Expense).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).all()

    def get_by_category(self, category: str) -> List[Expense]:
        """Get expenses by category
        
        Args:
            category: Category name
            
        Returns:
            List of expenses
        """
        return self.db.query(Expense).filter(Expense.category == category).all()

    def get_last_n_days(self, days: int) -> List[Expense]:
        """Get expenses from last N days
        
        Args:
            days: Number of days
            
        Returns:
            List of expenses
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        return self.get_by_date_range(start_date, datetime.utcnow())

    def get_spending_by_category(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """Get spending by category
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of category spending data
        """
        results = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label("total"),
            func.count(Expense.id).label("count"),
        ).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).group_by(Expense.category).all()

        return [
            {
                "category": row[0],
                "total": row[1],
                "count": row[2],
                "average": row[1] / row[2] if row[2] > 0 else 0,
            }
            for row in results
        ]

    def get_total_spending(self, start_date: datetime, end_date: datetime) -> float:
        """Get total spending in period
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Total spending amount
        """
        result = self.db.query(func.sum(Expense.amount)).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).scalar()
        return result or 0.0

    def get_transaction_count(self, start_date: datetime, end_date: datetime) -> int:
        """Get transaction count in period
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            Number of transactions
        """
        return self.db.query(Expense).filter(
            and_(Expense.date >= start_date, Expense.date <= end_date)
        ).count()
