"""SQLAlchemy ORM models"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Expense(Base):
    """Expense database model"""

    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    merchant_name = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)
    confidence_score = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for performance
    __table_args__ = (
        Index("idx_category", "category"),
        Index("idx_date", "date"),
        Index("idx_merchant", "merchant_name"),
        Index("idx_created", "created_at"),
    )

    def __repr__(self):
        return f"<Expense(id={self.id}, merchant={self.merchant_name}, amount={self.amount}, category={self.category})>"
