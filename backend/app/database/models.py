"""SQLAlchemy ORM models for database tables"""

from datetime import datetime

from sqlalchemy import Column, Float, Integer, String, DateTime, Text

from .session import Base


class ExpenseORM(Base):
    """ORM model for expenses table"""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    merchant_name = Column(String(255), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)
    confidence_score = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ExpenseORM(id={self.id}, merchant={self.merchant_name}, amount={self.amount})>"
