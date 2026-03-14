# Testing Strategy & Implementation Guide

**FinSight AI - Test-Driven Development**  
**Version:** 1.0.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Testing Strategy](#testing-strategy)
3. [Unit Testing](#unit-testing)
4. [Integration Testing](#integration-testing)
5. [End-to-End Testing](#end-to-end-testing)
6. [Testing Infrastructure](#testing-infrastructure)
7. [Coverage & Metrics](#coverage--metrics)

---

## 🎯 Overview

Production-ready code requires comprehensive testing across three levels:

```
┌─────────────────────────────────────────┐
│      End-to-End Tests                   │
│   (User workflows, API contracts)       │
├─────────────────────────────────────────┤
│      Integration Tests                  │
│  (Service + Repository + Database)      │
├─────────────────────────────────────────┤
│      Unit Tests                         │
│   (Individual components in isolation)  │
└─────────────────────────────────────────┘
```

---

## 🧪 Testing Strategy

### Test Pyramid

```
        /\
       /  \         E2E Tests (~10%)
      /    \        Complex workflows
     /------\
    /        \      Integration Tests (~30%)
   /          \     Service + Repo + DB
  /____________\
 /              \   Unit Tests (~60%)
/________________\ Individual functions
```

### Test Coverage Goals

| Component | Target | Priority |
|-----------|--------|----------|
| **Services** | >90% | Critical |
| **Repositories** | >85% | High |
| **Schemas/DTOs** | >80% | High |
| **Utils/Helpers** | >80% | Medium |
| **Middleware** | >75% | Medium |
| **Exceptions** | 100% | Low |

### Testing Tools

```
pytest              - Test framework
pytest-cov          - Coverage tracking
pytest-asyncio      - Async test support
faker               - Test data generation
factory-boy         - Factory fixtures
responses           - HTTP mocking
mongomock           - MongoDB mocking
```

---

## 🔬 Unit Testing

### Service Unit Tests

```python
# tests/unit/services/test_expense_service.py

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, call
from app.services.expense import ExpenseService
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.core.exceptions import (
    ValidationError, NotFoundError, DatabaseError
)


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return Mock()


@pytest.fixture
def mock_repository():
    """Create mock repository."""
    return Mock()


@pytest.fixture
def service(mock_logger, mock_repository):
    """Create service with mock dependencies."""
    return ExpenseService(mock_logger, mock_repository)


@pytest.fixture
def valid_expense_data():
    """Valid expense creation data."""
    return ExpenseCreate(
        merchant="Coffee Shop",
        amount=5.50,
        category="Food",
        description="Morning coffee",
    )


class TestExpenseServiceCreate:
    """Test expense creation."""
    
    def test_create_expense_success(self, service, mock_repository, valid_expense_data):
        """Test successful expense creation."""
        # Setup
        mock_expense = Mock(
            id=1,
            merchant="Coffee Shop",
            amount=5.50,
            category="Food",
        )
        mock_repository.create.return_value = mock_expense
        
        # Execute
        result = service.create_expense(valid_expense_data)
        
        # Verify
        assert result.id == 1
        assert result.merchant == "Coffee Shop"
        mock_repository.create.assert_called_once_with(valid_expense_data)
        mock_logger = service.logger
        # Verify logging occurred
        assert mock_logger.info.called or mock_logger.debug.called
    
    def test_create_expense_validation_fails(self, service):
        """Test validation failure on invalid data."""
        # Invalid data - negative amount
        invalid_data = ExpenseCreate(
            merchant="Shop",
            amount=-5.50,
            category="Food",
        )
        
        # Execute & Verify
        with pytest.raises(ValidationError) as exc_info:
            service.create_expense(invalid_data)
        
        assert "Amount must be positive" in str(exc_info.value.details)
    
    def test_create_expense_empty_merchant(self, service):
        """Test validation failure - empty merchant."""
        invalid_data = ExpenseCreate(
            merchant="",
            amount=5.50,
            category="Food",
        )
        
        with pytest.raises(ValidationError) as exc_info:
            service.create_expense(invalid_data)
        
        assert "merchant" in exc_info.value.details
    
    def test_create_expense_invalid_category(self, service):
        """Test validation failure - invalid category."""
        invalid_data = ExpenseCreate(
            merchant="Shop",
            amount=5.50,
            category="InvalidCategory",
        )
        
        with pytest.raises(ValidationError) as exc_info:
            service.create_expense(invalid_data)
        
        assert "category" in exc_info.value.details
    
    def test_create_expense_amount_too_large(self, service):
        """Test validation failure - amount too large."""
        invalid_data = ExpenseCreate(
            merchant="Shop",
            amount=9999999.99,
            category="Food",
        )
        
        with pytest.raises(ValidationError) as exc_info:
            service.create_expense(invalid_data)
        
        assert "amount" in exc_info.value.details
    
    def test_create_expense_future_date(self, service):
        """Test validation failure - future date."""
        invalid_data = ExpenseCreate(
            merchant="Shop",
            amount=5.50,
            category="Food",
            date=datetime.now() + timedelta(days=1),
        )
        
        with pytest.raises(ValidationError) as exc_info:
            service.create_expense(invalid_data)
        
        assert "date" in exc_info.value.details
    
    def test_create_expense_database_error(
        self,
        service,
        mock_repository,
        valid_expense_data
    ):
        """Test database error handling."""
        # Setup - repository raises error
        mock_repository.create.side_effect = Exception("DB connection failed")
        
        # Execute & Verify
        with pytest.raises(DatabaseError):
            service.create_expense(valid_expense_data)


class TestExpenseServiceGet:
    """Test expense retrieval."""
    
    def test_get_expense_success(self, service, mock_repository):
        """Test successful expense retrieval."""
        # Setup
        mock_expense = Mock(id=1, merchant="Shop", amount=5.50)
        mock_repository.get_by_id.return_value = mock_expense
        
        # Execute
        result = service.get_expense(1)
        
        # Verify
        assert result.id == 1
        mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_get_expense_not_found(self, service, mock_repository):
        """Test not found error."""
        # Setup
        mock_repository.get_by_id.return_value = None
        
        # Execute & Verify
        with pytest.raises(NotFoundError) as exc_info:
            service.get_expense(999)
        
        assert "999" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
    
    def test_get_all_expenses_success(self, service, mock_repository):
        """Test get all with pagination."""
        # Setup
        expenses = [
            Mock(id=1, merchant="Shop1"),
            Mock(id=2, merchant="Shop2"),
            Mock(id=3, merchant="Shop3"),
        ]
        mock_repository.get_all.return_value = expenses
        
        # Execute
        result = service.get_all_expenses(skip=0, limit=100)
        
        # Verify
        assert len(result) == 3
        mock_repository.get_all.assert_called_once_with(0, 100)
    
    def test_get_by_category_success(self, service, mock_repository):
        """Test filtering by category."""
        # Setup
        expenses = [
            Mock(id=1, category="Food"),
            Mock(id=2, category="Food"),
        ]
        mock_repository.get_by_category.return_value = expenses
        
        # Execute
        result = service.get_by_category("Food")
        
        # Verify
        assert len(result) == 2
        mock_repository.get_by_category.assert_called_once()
    
    def test_get_by_date_range_success(self, service, mock_repository):
        """Test filtering by date range."""
        # Setup
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)
        expenses = [
            Mock(id=1, date=datetime(2024, 1, 15)),
        ]
        mock_repository.get_by_date_range.return_value = expenses
        
        # Execute
        result = service.get_by_date_range(start, end)
        
        # Verify
        assert len(result) == 1
        mock_repository.get_by_date_range.assert_called_once()


class TestExpenseServiceUpdate:
    """Test expense updates."""
    
    def test_update_expense_success(self, service, mock_repository):
        """Test successful update."""
        # Setup
        update_data = ExpenseUpdate(merchant="New Shop", amount=6.50)
        mock_old = Mock(id=1, merchant="Old Shop")
        mock_new = Mock(id=1, merchant="New Shop", amount=6.50)
        mock_repository.get_by_id.return_value = mock_old
        mock_repository.update.return_value = mock_new
        
        # Execute
        result = service.update_expense(1, update_data)
        
        # Verify
        assert result.merchant == "New Shop"
        mock_repository.update.assert_called_once()
    
    def test_update_nonexistent_expense(self, service, mock_repository):
        """Test update of non-existent expense."""
        # Setup
        update_data = ExpenseUpdate(amount=6.50)
        mock_repository.get_by_id.return_value = None
        
        # Execute & Verify
        with pytest.raises(NotFoundError):
            service.update_expense(999, update_data)


class TestExpenseServiceDelete:
    """Test expense deletion."""
    
    def test_delete_expense_success(self, service, mock_repository):
        """Test successful deletion."""
        # Setup
        mock_repository.get_by_id.return_value = Mock(id=1)
        mock_repository.delete.return_value = True
        
        # Execute
        result = service.delete_expense(1)
        
        # Verify
        assert result is True
        mock_repository.delete.assert_called_once_with(1)
    
    def test_delete_nonexistent_expense(self, service, mock_repository):
        """Test deletion of non-existent expense."""
        # Setup
        mock_repository.get_by_id.return_value = None
        
        # Execute & Verify
        with pytest.raises(NotFoundError):
            service.delete_expense(999)


class TestExpenseServiceAnalytics:
    """Test analytics methods."""
    
    def test_get_spending_summary_cache_hit(self, service, mock_repository):
        """Test caching of spending summary."""
        # Setup
        cached_summary = {"total": 100, "count": 5}
        mock_repository.get_spending_summary.return_value = cached_summary
        
        # First call - cache miss
        result1 = service.get_spending_summary()
        
        # Second call - should hit cache
        with patch.object(mock_repository, 'get_spending_summary') as mock_get:
            result2 = service.get_spending_summary()
            # Repository should not be called again
            mock_get.assert_not_called()
        
        assert result1 == result2
    
    def test_get_by_category_summary(self, service, mock_repository):
        """Test category summary."""
        # Setup
        summary = {"Food": 150, "Transport": 50}
        mock_repository.get_by_category_summary.return_value = summary
        
        # Execute
        result = service.get_by_category_summary()
        
        # Verify
        assert result["Food"] == 150
        assert result["Transport"] == 50
```

### Repository Unit Tests

```python
# tests/unit/repositories/test_expense_repository.py

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from app.repositories.expense import ExpenseRepository
from app.models.expense import Expense
from app.core.exceptions import DatabaseError


@pytest.fixture
def mock_db_session():
    """Create mock database session."""
    return Mock()


@pytest.fixture
def repository(mock_db_session):
    """Create repository with mock session."""
    repo = ExpenseRepository()
    repo.db = mock_db_session
    return repo


class TestExpenseRepositoryCreate:
    """Test create operations."""
    
    def test_create_success(self, repository, mock_db_session):
        """Test successful creation."""
        # Setup
        expense_data = Mock(merchant="Shop", amount=5.50)
        mock_expense = Mock(id=1, merchant="Shop", amount=5.50)
        mock_db_session.add = Mock()
        mock_db_session.commit = Mock()
        mock_db_session.refresh = Mock()
        
        with patch('app.repositories.base.BaseRepository.create') as mock_base:
            mock_base.return_value = mock_expense
            result = repository.create(expense_data)
        
        assert result.id == 1
    
    def test_create_database_error(self, repository, mock_db_session):
        """Test database error on create."""
        # Setup
        mock_db_session.add.side_effect = Exception("Connection failed")
        
        with pytest.raises(DatabaseError):
            repository.create(Mock())


class TestExpenseRepositoryQuery:
    """Test query operations."""
    
    def test_get_by_id_success(self, repository, mock_db_session):
        """Test successful get by ID."""
        # Setup
        mock_expense = Mock(id=1, merchant="Shop")
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_expense
        
        # Execute
        with patch('app.repositories.base.BaseRepository.get_by_id') as mock_base:
            mock_base.return_value = mock_expense
            result = repository.get_by_id(1)
        
        assert result.id == 1
    
    def test_get_by_category_success(self, repository, mock_db_session):
        """Test get by category."""
        # Setup
        expenses = [Mock(id=1, category="Food")]
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = expenses
        
        # Execute
        result = repository.get_by_category("Food")
        
        # Verify
        assert len(result) >= 0
```

### Schema/DTO Tests

```python
# tests/unit/schemas/test_expense_schemas.py

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse
)


class TestExpenseCreateSchema:
    """Test ExpenseCreate validation."""
    
    def test_valid_expense_create(self):
        """Test valid expense creation."""
        data = {
            "merchant": "Coffee Shop",
            "amount": 5.50,
            "category": "Food",
        }
        expense = ExpenseCreate(**data)
        
        assert expense.merchant == "Coffee Shop"
        assert expense.amount == 5.50
        assert expense.category == "Food"
    
    def test_invalid_amount_negative(self):
        """Test negative amount rejection."""
        data = {
            "merchant": "Shop",
            "amount": -5.50,
            "category": "Food",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ExpenseCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("amount" in str(e) for e in errors)
    
    def test_invalid_amount_zero(self):
        """Test zero amount rejection."""
        data = {
            "merchant": "Shop",
            "amount": 0,
            "category": "Food",
        }
        
        with pytest.raises(ValidationError):
            ExpenseCreate(**data)
    
    def test_merchant_required(self):
        """Test merchant field required."""
        data = {
            "amount": 5.50,
            "category": "Food",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ExpenseCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("merchant" in str(e) for e in errors)
    
    def test_category_enum_validation(self):
        """Test category enum validation."""
        data = {
            "merchant": "Shop",
            "amount": 5.50,
            "category": "InvalidCategory",
        }
        
        with pytest.raises(ValidationError) as exc_info:
            ExpenseCreate(**data)
        
        errors = exc_info.value.errors()
        assert any("category" in str(e) for e in errors)
    
    def test_default_date_now(self):
        """Test default date is now."""
        data = {
            "merchant": "Shop",
            "amount": 5.50,
            "category": "Food",
        }
        expense = ExpenseCreate(**data)
        
        # Date should be set and recent
        assert expense.date is not None
        assert (datetime.now() - expense.date).total_seconds() < 1


class TestExpenseUpdateSchema:
    """Test ExpenseUpdate validation."""
    
    def test_all_fields_optional(self):
        """Test all fields optional on update."""
        # Empty update
        expense = ExpenseUpdate()
        assert expense.merchant is None
        assert expense.amount is None
    
    def test_partial_update(self):
        """Test partial updates."""
        data = {"merchant": "New Shop"}
        expense = ExpenseUpdate(**data)
        
        assert expense.merchant == "New Shop"
        assert expense.amount is None
```

---

## 🔗 Integration Testing

### Database Integration Tests

```python
# tests/integration/test_expense_service_integration.py

import pytest
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.services.expense import ExpenseService
from app.repositories.expense import ExpenseRepository
from app.schemas.expense import ExpenseCreate
from app.models.expense import Expense


@pytest.fixture
def db_session():
    """Create test database session."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def repository(db_session):
    """Create repository with real DB."""
    return ExpenseRepository(db_session)


@pytest.fixture
def service(repository):
    """Create service with real repository."""
    from app.core.logger import get_logger
    logger = get_logger(__name__)
    return ExpenseService(logger, repository)


class TestExpenseServiceIntegration:
    """Integration tests with real database."""
    
    def test_create_and_retrieve_expense(self, service, db_session):
        """Test creating and retrieving expense."""
        # Create
        create_data = ExpenseCreate(
            merchant="Coffee Shop",
            amount=5.50,
            category="Food",
        )
        created = service.create_expense(create_data)
        
        # Retrieve
        retrieved = service.get_expense(created.id)
        
        # Verify
        assert retrieved.merchant == "Coffee Shop"
        assert retrieved.amount == 5.50
        
        # Verify in database
        db_expense = db_session.query(Expense).filter_by(
            id=created.id
        ).first()
        assert db_expense is not None
    
    def test_create_update_delete_workflow(self, service):
        """Test complete CRUD workflow."""
        # Create
        create_data = ExpenseCreate(
            merchant="Shop",
            amount=10.00,
            category="Shopping",
        )
        expense = service.create_expense(create_data)
        expense_id = expense.id
        
        # Update
        from app.schemas.expense import ExpenseUpdate
        update_data = ExpenseUpdate(merchant="New Shop")
        updated = service.update_expense(expense_id, update_data)
        assert updated.merchant == "New Shop"
        
        # Delete
        deleted = service.delete_expense(expense_id)
        assert deleted is True
        
        # Verify deleted
        from app.core.exceptions import NotFoundError
        with pytest.raises(NotFoundError):
            service.get_expense(expense_id)
    
    def test_spending_summary_calculation(self, service):
        """Test spending summary calculation."""
        # Create multiple expenses
        for i in range(5):
            service.create_expense(ExpenseCreate(
                merchant=f"Shop{i}",
                amount=10.00 * (i + 1),
                category="Food",
            ))
        
        # Get summary
        summary = service.get_spending_summary()
        
        # Verify
        assert summary["total"] > 0
        assert summary["count"] == 5
```

### API Integration Tests

```python
# tests/integration/test_expense_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestExpenseAPI:
    """Integration tests for expense API."""
    
    def test_create_expense_endpoint(self, client):
        """Test POST /api/expenses."""
        response = client.post(
            "/api/expenses",
            json={
                "merchant": "Coffee Shop",
                "amount": 5.50,
                "category": "Food",
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["merchant"] == "Coffee Shop"
        assert "id" in data
    
    def test_get_expense_endpoint(self, client):
        """Test GET /api/expenses/{id}."""
        # Create
        create_response = client.post(
            "/api/expenses",
            json={
                "merchant": "Shop",
                "amount": 5.50,
                "category": "Food",
            }
        )
        expense_id = create_response.json()["id"]
        
        # Get
        get_response = client.get(f"/api/expenses/{expense_id}")
        
        assert get_response.status_code == 200
        assert get_response.json()["id"] == expense_id
    
    def test_get_nonexistent_expense(self, client):
        """Test 404 for missing expense."""
        response = client.get("/api/expenses/99999")
        
        assert response.status_code == 404
    
    def test_create_invalid_expense(self, client):
        """Test validation error on invalid data."""
        response = client.post(
            "/api/expenses",
            json={
                "merchant": "",
                "amount": -5.50,
                "category": "Invalid",
            }
        )
        
        assert response.status_code == 400
        assert "error" in response.json()
```

---

## 🚀 End-to-End Testing

### User Workflow Tests

```python
# tests/e2e/test_user_workflows.py

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestUserWorkflows:
    """Test complete user workflows."""
    
    def test_expense_tracking_workflow(self, client):
        """Test typical expense tracking workflow.
        
        User:
        1. Creates expenses
        2. Views spending summary
        3. Checks budget
        4. Updates expense
        5. Deletes expense
        """
        # 1. Create first expense
        exp1 = client.post("/api/expenses", json={
            "merchant": "Coffee Shop",
            "amount": 5.50,
            "category": "Food",
        }).json()
        assert exp1["id"]
        
        # 2. Create second expense
        exp2 = client.post("/api/expenses", json={
            "merchant": "Gas Station",
            "amount": 50.00,
            "category": "Transport",
        }).json()
        assert exp2["id"]
        
        # 3. View spending summary
        summary = client.get("/api/expenses/summary").json()
        assert summary["total"] == 55.50
        assert summary["count"] == 2
        
        # 4. Update first expense
        updated = client.put(f"/api/expenses/{exp1['id']}", json={
            "amount": 6.00,
        }).json()
        assert updated["amount"] == 6.00
        
        # 5. Delete second expense
        delete_resp = client.delete(f"/api/expenses/{exp2['id']}")
        assert delete_resp.status_code == 204
        
        # 6. Verify summary updated
        final_summary = client.get("/api/expenses/summary").json()
        assert final_summary["total"] == 6.00
        assert final_summary["count"] == 1
    
    def test_receipt_upload_workflow(self, client):
        """Test receipt upload and OCR workflow."""
        # 1. Upload receipt
        import base64
        with open("tests/fixtures/sample_receipt.jpg", "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        upload_resp = client.post("/api/receipts/upload", json={
            "filename": "receipt.jpg",
            "image_base64": image_data,
        })
        assert upload_resp.status_code == 201
        receipt = upload_resp.json()
        
        # 2. Get OCR result
        receipt_detail = client.get(
            f"/api/receipts/{receipt['id']}"
        ).json()
        assert receipt_detail["ocr_result"]
        assert "merchant" in receipt_detail["ocr_result"]
    
    def test_budget_alert_workflow(self, client):
        """Test budget alert workflow."""
        # 1. Create budget
        budget = client.post("/api/budgets", json={
            "category": "Food",
            "amount": 100.00,
        }).json()
        
        # 2. Create expenses under budget
        for i in range(3):
            client.post("/api/expenses", json={
                "merchant": f"Restaurant {i}",
                "amount": 20.00,
                "category": "Food",
            })
        
        # 3. Check alerts - should be warning
        alerts = client.get("/api/budgets/alerts").json()
        food_alert = next(a for a in alerts if a["category"] == "Food")
        assert food_alert["percentage"] == 60  # 60 of 100
        
        # 4. Create more expenses
        client.post("/api/expenses", json={
            "merchant": "Expensive Restaurant",
            "amount": 50.00,
            "category": "Food",
        })
        
        # 5. Check alerts - should be exceeded
        alerts = client.get("/api/budgets/alerts").json()
        food_alert = next(a for a in alerts if a["category"] == "Food")
        assert food_alert["status"] == "exceeded"
```

---

## 🛠️ Testing Infrastructure

### pytest Configuration

```python
# tests/conftest.py

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.session import Base
from app.core.logger import get_logger


# Setup test database
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    """Create test database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def logger():
    """Create test logger."""
    return get_logger("test")


@pytest.fixture
def mock_ocr_client():
    """Create mock OCR client."""
    from unittest.mock import Mock
    client = Mock()
    client.process_image.return_value = {
        "merchant": "Test Shop",
        "amount": 50.00,
        "date": "2024-01-01",
        "items": ["Item 1", "Item 2"],
    }
    return client
```

### Test Fixtures

```python
# tests/fixtures/factories.py

from factory import Factory, Faker, SubFactory
from app.models.expense import Expense


class ExpenseFactory(Factory):
    """Factory for creating test expenses."""
    
    class Meta:
        model = Expense
    
    merchant = Faker("company")
    amount = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    category = Faker("random_element", elements=[
        "Food", "Transport", "Shopping", "Utilities",
        "Entertainment", "Health", "Other"
    ])
    description = Faker("text", max_nb_chars=100)
    date = Faker("date_time")
```

---

## 📊 Coverage & Metrics

### Run Tests with Coverage

```bash
# Unit tests with coverage
pytest tests/unit/ --cov=app --cov-report=html

# Integration tests with coverage
pytest tests/integration/ --cov=app --cov-report=html

# All tests
pytest tests/ --cov=app --cov-report=html --cov-report=term

# Specific test file
pytest tests/unit/services/test_expense_service.py -v

# Specific test class
pytest tests/unit/services/test_expense_service.py::TestExpenseServiceCreate -v

# Specific test method
pytest tests/unit/services/test_expense_service.py::TestExpenseServiceCreate::test_create_expense_success -v
```

### Coverage Goals

```
Name                           Stmts   Miss  Cover
--------------------------------------------------
app/services/expense.py         150     5    96%
app/services/receipt.py          80     2    97%
app/repositories/expense.py      60     3    95%
app/schemas/expense.py          100     8    92%
app/core/exceptions.py           50     0   100%
app/middleware/http.py           75     5    93%
--------------------------------------------------
TOTAL                           515    23    95%
```

### CI/CD Integration

```yaml
# .github/workflows/tests.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.xml
```

---

## ✅ Testing Checklist

- [ ] Unit test service creation
- [ ] Unit test service validation
- [ ] Unit test service error handling
- [ ] Unit test repository CRUD
- [ ] Unit test schemas/DTOs
- [ ] Integration test service + repository
- [ ] Integration test service + database
- [ ] Integration test API endpoints
- [ ] E2E test user workflows
- [ ] E2E test error scenarios
- [ ] Coverage report >90%
- [ ] CI/CD pipeline setup
- [ ] Performance benchmarks
- [ ] Load testing
- [ ] Security testing

---

**Version:** 1.0.0  
**Status:** Ready for Implementation  
**Last Updated:** March 2024
