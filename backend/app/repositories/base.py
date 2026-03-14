"""
Base repository class for data access patterns.

This module provides a base repository class implementing the Repository
pattern for consistent, reusable data access operations.

Examples:
    Creating a repository:
        class ExpenseRepository(BaseRepository):
            model = Expense
            
            def get_by_category(self, category):
                return self.query().filter(
                    self.model.category == category
                ).all()
"""

from typing import Any, Generic, List, Optional, Type, TypeVar
from abc import ABC, abstractmethod

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository for data access operations.
    
    Implements common CRUD operations and query patterns.
    
    Attributes:
        db: SQLAlchemy session
        model: SQLAlchemy model class
    """

    db: Session
    model: Type[T]

    def __init__(self, db: Session):
        """Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def create(self, obj: T) -> T:
        """Create new record.
        
        Args:
            obj: Object to create
            
        Returns:
            Created object with ID
            
        Raises:
            SQLAlchemyError: If creation fails
        """
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def get_by_id(self, id: Any) -> Optional[T]:
        """Get record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Record or None if not found
        """
        return self.db.query(self.model).filter(
            self.model.id == id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of records
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: Any, obj: T) -> T:
        """Update existing record.
        
        Args:
            id: Record ID
            obj: Updated object data
            
        Returns:
            Updated object
            
        Raises:
            SQLAlchemyError: If update fails
        """
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                return None
            
            for key, value in obj.dict(exclude_unset=True).items():
                setattr(db_obj, key, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def delete(self, id: Any) -> bool:
        """Delete record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            SQLAlchemyError: If deletion fails
        """
        try:
            obj = self.get_by_id(id)
            if not obj:
                return False
            
            self.db.delete(obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def exists(self, id: Any) -> bool:
        """Check if record exists.
        
        Args:
            id: Record ID
            
        Returns:
            True if exists, False otherwise
        """
        return self.db.query(
            self.db.query(self.model).filter(
                self.model.id == id
            ).exists()
        ).scalar()

    def count(self) -> int:
        """Get total count of records.
        
        Returns:
            Total record count
        """
        return self.db.query(self.model).count()

    def query(self):
        """Get query builder for custom queries.
        
        Returns:
            SQLAlchemy query object
        """
        return self.db.query(self.model)

    def bulk_create(self, objs: List[T]) -> List[T]:
        """Create multiple records.
        
        Args:
            objs: List of objects to create
            
        Returns:
            List of created objects
            
        Raises:
            SQLAlchemyError: If creation fails
        """
        try:
            self.db.bulk_save_objects(objs)
            self.db.commit()
            return objs
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e

    def bulk_delete(self, ids: List[Any]) -> int:
        """Delete multiple records.
        
        Args:
            ids: List of record IDs
            
        Returns:
            Number of deleted records
            
        Raises:
            SQLAlchemyError: If deletion fails
        """
        try:
            count = self.db.query(self.model).filter(
                self.model.id.in_(ids)
            ).delete(synchronize_session=False)
            self.db.commit()
            return count
        except SQLAlchemyError as e:
            self.db.rollback()
            raise e
