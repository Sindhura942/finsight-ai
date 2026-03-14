"""Test configuration and fixtures"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.session import Base
from app.database.repository import ExpenseRepository


@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_repository(test_db):
    """Create test repository"""
    return ExpenseRepository(test_db)
