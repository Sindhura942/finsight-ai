"""Tests for expense repository"""

import pytest
from datetime import datetime, timedelta

from app.models import ExpenseCreate
from app.database.repository import ExpenseRepository


def test_create_expense(test_repository):
    """Test creating an expense"""
    expense = ExpenseCreate(
        merchant_name="Starbucks",
        amount=5.50,
        category="Food & Dining",
    )
    
    created = test_repository.create(expense)
    
    assert created.id is not None
    assert created.merchant_name == "Starbucks"
    assert created.amount == 5.50


def test_get_by_id(test_repository):
    """Test getting expense by ID"""
    expense = ExpenseCreate(
        merchant_name="Coffee Shop",
        amount=3.50,
        category="Food & Dining",
    )
    
    created = test_repository.create(expense)
    retrieved = test_repository.get_by_id(created.id)
    
    assert retrieved is not None
    assert retrieved.merchant_name == "Coffee Shop"


def test_delete_expense(test_repository):
    """Test deleting an expense"""
    expense = ExpenseCreate(
        merchant_name="Restaurant",
        amount=25.00,
        category="Food & Dining",
    )
    
    created = test_repository.create(expense)
    deleted = test_repository.delete(created.id)
    
    assert deleted is True
    assert test_repository.get_by_id(created.id) is None


def test_get_all(test_repository):
    """Test getting all expenses"""
    for i in range(5):
        expense = ExpenseCreate(
            merchant_name=f"Store {i}",
            amount=10.0 + i,
            category="Shopping",
        )
        test_repository.create(expense)
    
    all_expenses = test_repository.get_all()
    assert len(all_expenses) == 5


def test_get_spending_by_category(test_repository):
    """Test getting spending by category"""
    expenses = [
        ExpenseCreate(merchant_name="Coffee", amount=5.0, category="Food & Dining"),
        ExpenseCreate(merchant_name="Lunch", amount=15.0, category="Food & Dining"),
        ExpenseCreate(merchant_name="Uber", amount=20.0, category="Transportation"),
    ]
    
    for exp in expenses:
        test_repository.create(exp)
    
    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow() + timedelta(days=1)
    
    results = test_repository.get_spending_by_category(start, end)
    
    assert len(results) == 2
    
    food = next(r for r in results if r['category'] == 'Food & Dining')
    assert food['total'] == 20.0
    assert food['count'] == 2
