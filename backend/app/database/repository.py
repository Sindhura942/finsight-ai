"""Repository pattern for database operations"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models import ExpenseCreate, ExpenseUpdate
from .models import ExpenseORM


class ExpenseRepository:
    """Repository for expense database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, expense: ExpenseCreate) -> ExpenseORM:
        """Create a new expense"""
        db_expense = ExpenseORM(**expense.model_dump())
        self.db.add(db_expense)
        self.db.commit()
        self.db.refresh(db_expense)
        return db_expense

    def get_by_id(self, expense_id: int) -> Optional[ExpenseORM]:
        """Get expense by ID"""
        return self.db.query(ExpenseORM).filter(ExpenseORM.id == expense_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ExpenseORM]:
        """Get all expenses with pagination"""
        return self.db.query(ExpenseORM).offset(skip).limit(limit).all()

    def update(self, expense_id: int, expense_update: ExpenseUpdate) -> Optional[ExpenseORM]:
        """Update an expense"""
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
        """Delete an expense"""
        db_expense = self.get_by_id(expense_id)
        if not db_expense:
            return False

        self.db.delete(db_expense)
        self.db.commit()
        return True

    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[ExpenseORM]:
        """Get expenses within a date range"""
        return self.db.query(ExpenseORM).filter(
            and_(ExpenseORM.date >= start_date, ExpenseORM.date <= end_date)
        ).all()

    def get_by_category(self, category: str) -> List[ExpenseORM]:
        """Get expenses by category"""
        return self.db.query(ExpenseORM).filter(ExpenseORM.category == category).all()

    def get_last_n_days(self, days: int) -> List[ExpenseORM]:
        """Get expenses from last N days"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return self.get_by_date_range(start_date, datetime.utcnow())

    def get_spending_by_category(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """Get total spending by category"""
        results = self.db.query(
            ExpenseORM.category,
            func.sum(ExpenseORM.amount).label("total"),
            func.count(ExpenseORM.id).label("count"),
        ).filter(
            and_(ExpenseORM.date >= start_date, ExpenseORM.date <= end_date)
        ).group_by(ExpenseORM.category).all()

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
        """Get total spending in a date range"""
        result = self.db.query(func.sum(ExpenseORM.amount)).filter(
            and_(ExpenseORM.date >= start_date, ExpenseORM.date <= end_date)
        ).scalar()
        return result or 0.0

    def get_transaction_count(self, start_date: datetime, end_date: datetime) -> int:
        """Get transaction count in a date range"""
        return self.db.query(ExpenseORM).filter(
            and_(ExpenseORM.date >= start_date, ExpenseORM.date <= end_date)
        ).count()
