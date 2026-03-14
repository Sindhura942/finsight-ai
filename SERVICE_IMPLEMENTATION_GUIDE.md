# Service Implementation Guide

**FinSight AI - Service Layer Development**  
**Version:** 1.0.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Service Patterns](#service-patterns)
3. [ExpenseService](#expenseservice)
4. [ReceiptService](#receiptservice)
5. [AnalyticsService](#analyticsservice)
6. [Testing Services](#testing-services)
7. [Common Patterns](#common-patterns)

---

## 🎯 Overview

The service layer implements business logic by:

1. **Validation** - Validate input data
2. **Processing** - Transform and process data
3. **Orchestration** - Coordinate multiple operations
4. **Error Handling** - Catch and handle errors
5. **Logging** - Log all operations

### Service Architecture

```
API Route
    ↓ (request data)
Service (ExpenseService, ReceiptService, etc.)
    ├─ Validate input
    ├─ Call repository/external services
    ├─ Process result
    └─ Return response
    ↓ (response data)
API Response
```

---

## 🔧 Service Patterns

### Pattern 1: Basic Service

```python
from app.services.base import BaseService
from app.core.exceptions import ValidationError
from app.core.logger import get_logger

class BasicService(BaseService):
    """Example service implementing basic operations."""
    
    def __init__(self, logger, repository):
        """Initialize with dependencies.
        
        Args:
            logger: Logger instance
            repository: Data repository
        """
        super().__init__(logger, repository)
    
    def get_by_id(self, id: int):
        """Get single item by ID."""
        self._log_operation("Getting item", item_id=id)
        
        item = self._call_repository(
            self.repository.get_by_id,
            id
        )
        
        if not item:
            raise NotFoundError(f"Item {id} not found")
        
        return item
    
    def get_all(self, skip: int = 0, limit: int = 100):
        """Get all items with pagination."""
        self._log_operation(
            "Getting items",
            skip=skip,
            limit=limit
        )
        
        items = self._call_repository(
            self.repository.get_all,
            skip, limit
        )
        
        return items
```

### Pattern 2: Validation Service

```python
class ValidatingService(BaseService):
    """Service with comprehensive validation."""
    
    def validate_data(self, data):
        """Validate data before processing.
        
        Args:
            data: Data to validate
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Validate fields
        if not data.merchant or not data.merchant.strip():
            errors["merchant"] = "Merchant required"
        
        if data.amount <= 0:
            errors["amount"] = "Amount must be positive"
        
        if data.amount > 1000000:
            errors["amount"] = "Amount too large"
        
        if errors:
            raise ValidationError(
                "Data validation failed",
                details=errors
            )
    
    def create_item(self, data):
        """Create item with validation."""
        self.validate_data(data)
        
        return self._call_repository(
            self.repository.create,
            data
        )
```

### Pattern 3: Caching Service

```python
from app.services.base import CacheableService

class CachingService(CacheableService):
    """Service with caching support."""
    
    def get_summary(self, user_id: int, force_refresh=False):
        """Get summary with caching.
        
        Args:
            user_id: User ID
            force_refresh: Skip cache
            
        Returns:
            Cached or fresh summary
        """
        cache_key = f"summary:{user_id}"
        
        if not force_refresh:
            cached = self.get_cached(cache_key)
            if cached:
                self.logger.debug("Cache hit", extra={"key": cache_key})
                return cached
        
        # Fetch fresh data
        summary = self._call_repository(
            self.repository.get_summary,
            user_id
        )
        
        # Cache result
        self.set_cache(cache_key, summary)
        
        self.logger.debug("Cache miss", extra={"key": cache_key})
        
        return summary
```

### Pattern 4: Transaction Service

```python
from app.services.base import TransactionService

class TransactionalService(TransactionService):
    """Service with transaction support."""
    
    def transfer_budget(self, from_id: int, to_id: int, amount: float):
        """Transfer budget between accounts in transaction.
        
        Args:
            from_id: Source account ID
            to_id: Target account ID
            amount: Amount to transfer
            
        Returns:
            Transfer result
        """
        def transfer_logic():
            # Get accounts
            from_account = self._call_repository(
                self.repository.get_by_id,
                from_id
            )
            to_account = self._call_repository(
                self.repository.get_by_id,
                to_id
            )
            
            # Validate
            if from_account.balance < amount:
                raise ValidationError(
                    "Insufficient balance",
                    details={"available": from_account.balance}
                )
            
            # Update accounts (in transaction)
            from_account.balance -= amount
            to_account.balance += amount
            
            updated_from = self._call_repository(
                self.repository.update,
                from_id,
                from_account
            )
            updated_to = self._call_repository(
                self.repository.update,
                to_id,
                to_account
            )
            
            return {"from": updated_from, "to": updated_to}
        
        # Execute in transaction
        return self.execute_in_transaction(transfer_logic)
```

---

## 💰 ExpenseService

### Implementation

```python
from typing import List
from datetime import datetime, timedelta
from app.services.base import CacheableService
from app.schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse
)
from app.core.exceptions import (
    ValidationError, NotFoundError, BusinessLogicError
)
from app.core.logger import get_logger

class ExpenseService(CacheableService):
    """Service for expense management.
    
    Handles:
    - Creating and updating expenses
    - Expense retrieval and filtering
    - Budget tracking
    - Spending analysis
    - Receipt processing
    """
    
    CACHE_TTL = 300  # 5 minutes
    
    def __init__(self, logger, repository):
        """Initialize expense service.
        
        Args:
            logger: Logger instance
            repository: ExpenseRepository instance
        """
        super().__init__(logger, repository)
    
    # ========== CRUD Operations ==========
    
    def create_expense(self, expense_data: ExpenseCreate) -> ExpenseResponse:
        """Create new expense.
        
        Args:
            expense_data: Expense creation data
            
        Returns:
            Created expense
            
        Raises:
            ValidationError: If data invalid
            DatabaseError: If save fails
        """
        self._log_operation(
            "Creating expense",
            merchant=expense_data.merchant,
            amount=expense_data.amount,
            category=expense_data.category,
        )
        
        # Validate
        self._validate_expense(expense_data)
        
        # Create
        expense = self._call_repository(
            self.repository.create,
            expense_data
        )
        
        # Clear cache
        self.clear_cache("summary:*")
        
        self.logger.info(
            "Expense created",
            extra={"expense_id": expense.id, "amount": expense.amount}
        )
        
        return expense
    
    def get_expense(self, expense_id: int) -> ExpenseResponse:
        """Get expense by ID.
        
        Args:
            expense_id: Expense ID
            
        Returns:
            Expense details
            
        Raises:
            NotFoundError: If not found
        """
        self._log_operation("Getting expense", expense_id=expense_id)
        
        expense = self._call_repository(
            self.repository.get_by_id,
            expense_id
        )
        
        if not expense:
            raise NotFoundError(
                f"Expense {expense_id} not found",
                resource_type="Expense",
                resource_id=expense_id
            )
        
        return expense
    
    def get_all_expenses(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ExpenseResponse]:
        """Get all expenses with pagination.
        
        Args:
            skip: Records to skip
            limit: Records to return
            
        Returns:
            List of expenses
        """
        self._log_operation(
            "Getting expenses",
            skip=skip,
            limit=limit
        )
        
        expenses = self._call_repository(
            self.repository.get_all,
            skip, limit
        )
        
        return expenses
    
    def update_expense(
        self,
        expense_id: int,
        expense_data: ExpenseUpdate,
    ) -> ExpenseResponse:
        """Update expense.
        
        Args:
            expense_id: Expense ID
            expense_data: Update data
            
        Returns:
            Updated expense
            
        Raises:
            NotFoundError: If not found
            ValidationError: If data invalid
        """
        self._log_operation(
            "Updating expense",
            expense_id=expense_id,
        )
        
        # Check exists
        expense = self.get_expense(expense_id)
        
        # Validate
        self._validate_expense(expense_data, is_update=True)
        
        # Update
        updated = self._call_repository(
            self.repository.update,
            expense_id,
            expense_data
        )
        
        # Clear cache
        self.clear_cache("summary:*")
        
        self.logger.info(
            "Expense updated",
            extra={"expense_id": expense_id}
        )
        
        return updated
    
    def delete_expense(self, expense_id: int) -> bool:
        """Delete expense.
        
        Args:
            expense_id: Expense ID
            
        Returns:
            Success status
            
        Raises:
            NotFoundError: If not found
        """
        self._log_operation(
            "Deleting expense",
            expense_id=expense_id
        )
        
        # Check exists
        self.get_expense(expense_id)
        
        # Delete
        success = self._call_repository(
            self.repository.delete,
            expense_id
        )
        
        # Clear cache
        self.clear_cache("summary:*")
        
        if success:
            self.logger.info(
                "Expense deleted",
                extra={"expense_id": expense_id}
            )
        
        return success
    
    # ========== Filtering & Querying ==========
    
    def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ExpenseResponse]:
        """Get expenses by category.
        
        Args:
            category: Expense category
            skip: Records to skip
            limit: Records to return
            
        Returns:
            List of expenses in category
        """
        self._log_operation(
            "Getting expenses by category",
            category=category,
        )
        
        expenses = self._call_repository(
            self.repository.get_by_category,
            category, skip, limit
        )
        
        return expenses
    
    def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ExpenseResponse]:
        """Get expenses within date range.
        
        Args:
            start_date: Start date
            end_date: End date
            skip: Records to skip
            limit: Records to return
            
        Returns:
            List of expenses in range
        """
        self._log_operation(
            "Getting expenses by date range",
            start_date=start_date,
            end_date=end_date,
        )
        
        expenses = self._call_repository(
            self.repository.get_by_date_range,
            start_date, end_date, skip, limit
        )
        
        return expenses
    
    # ========== Analysis ==========
    
    def get_spending_summary(self, user_id: int = None) -> dict:
        """Get spending summary with caching.
        
        Args:
            user_id: User ID (optional)
            
        Returns:
            Summary statistics
        """
        cache_key = f"summary:{user_id}"
        
        # Try cache
        cached = self.get_cached(cache_key)
        if cached:
            self.logger.debug("Summary cache hit")
            return cached
        
        # Calculate
        self._log_operation("Calculating spending summary")
        
        summary = self._call_repository(
            self.repository.get_spending_summary,
            user_id
        )
        
        # Cache
        self.set_cache(cache_key, summary, ttl=600)
        
        return summary
    
    def get_by_category_summary(self, user_id: int = None) -> dict:
        """Get expenses grouped by category.
        
        Args:
            user_id: User ID (optional)
            
        Returns:
            Summary by category
        """
        self._log_operation(
            "Getting category summary",
            user_id=user_id
        )
        
        summary = self._call_repository(
            self.repository.get_by_category_summary,
            user_id
        )
        
        return summary
    
    def get_monthly_trend(self, months: int = 6) -> dict:
        """Get monthly spending trend.
        
        Args:
            months: Number of months to include
            
        Returns:
            Monthly trend data
        """
        self._log_operation(
            "Getting monthly trend",
            months=months
        )
        
        trend = self._call_repository(
            self.repository.get_monthly_trend,
            months
        )
        
        return trend
    
    # ========== Validation ==========
    
    def _validate_expense(
        self,
        expense_data: ExpenseCreate,
        is_update: bool = False,
    ) -> None:
        """Validate expense data.
        
        Args:
            expense_data: Data to validate
            is_update: Is this an update operation
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Merchant validation
        if hasattr(expense_data, 'merchant'):
            if not expense_data.merchant or not expense_data.merchant.strip():
                errors["merchant"] = "Merchant name required"
            elif len(expense_data.merchant) > 255:
                errors["merchant"] = "Merchant name too long"
        
        # Amount validation
        if hasattr(expense_data, 'amount'):
            if expense_data.amount <= 0:
                errors["amount"] = "Amount must be positive"
            elif expense_data.amount > 1000000:
                errors["amount"] = "Amount exceeds maximum"
        
        # Category validation
        if hasattr(expense_data, 'category'):
            valid_categories = [
                "Food", "Transport", "Shopping",
                "Utilities", "Entertainment", "Health", "Other"
            ]
            if expense_data.category not in valid_categories:
                errors["category"] = f"Invalid category: {expense_data.category}"
        
        # Date validation
        if hasattr(expense_data, 'date'):
            if expense_data.date > datetime.now():
                errors["date"] = "Date cannot be in future"
        
        if errors:
            raise ValidationError(
                "Expense validation failed",
                details=errors
            )
```

---

## 🧾 ReceiptService

### Implementation

```python
from typing import Optional
from app.services.base import BaseService
from app.schemas.expense import ReceiptUploadRequest, ReceiptAnalysisResult
from app.core.exceptions import (
    ValidationError, ExternalServiceError
)

class ReceiptService(BaseService):
    """Service for receipt processing.
    
    Handles:
    - Receipt upload and storage
    - OCR processing
    - Receipt data extraction
    - Receipt matching with expenses
    """
    
    def __init__(self, logger, repository, ocr_client=None):
        """Initialize receipt service.
        
        Args:
            logger: Logger instance
            repository: ReceiptRepository instance
            ocr_client: OCR client (optional)
        """
        super().__init__(logger, repository)
        self.ocr_client = ocr_client
    
    def upload_receipt(
        self,
        receipt_data: ReceiptUploadRequest,
        expense_id: Optional[int] = None,
    ) -> dict:
        """Upload and process receipt.
        
        Args:
            receipt_data: Receipt upload data
            expense_id: Associate with expense
            
        Returns:
            Receipt details with OCR result
            
        Raises:
            ValidationError: If data invalid
            ExternalServiceError: If OCR fails
        """
        self._log_operation(
            "Uploading receipt",
            filename=receipt_data.filename,
            expense_id=expense_id,
        )
        
        # Validate
        self._validate_receipt(receipt_data)
        
        # Store receipt
        receipt = self._call_repository(
            self.repository.create,
            {
                "filename": receipt_data.filename,
                "image_data": receipt_data.image_base64,
                "expense_id": expense_id,
            }
        )
        
        # Process with OCR
        ocr_result = None
        try:
            ocr_result = self.process_receipt_ocr(receipt.id)
        except ExternalServiceError as e:
            self.logger.warning(
                "OCR processing failed",
                extra={"receipt_id": receipt.id, "error": str(e)}
            )
        
        self.logger.info(
            "Receipt uploaded",
            extra={"receipt_id": receipt.id}
        )
        
        return {
            "receipt": receipt,
            "ocr_result": ocr_result,
        }
    
    def process_receipt_ocr(
        self,
        receipt_id: int,
    ) -> ReceiptAnalysisResult:
        """Process receipt with OCR.
        
        Args:
            receipt_id: Receipt ID
            
        Returns:
            OCR analysis result
            
        Raises:
            ExternalServiceError: If OCR fails
        """
        self._log_operation(
            "Processing receipt OCR",
            receipt_id=receipt_id
        )
        
        # Get receipt
        receipt = self._call_repository(
            self.repository.get_by_id,
            receipt_id
        )
        
        if not receipt:
            raise NotFoundError("Receipt not found")
        
        # Call OCR service
        if not self.ocr_client:
            raise ExternalServiceError(
                service="OCR",
                message="OCR service not configured"
            )
        
        try:
            ocr_result = self.ocr_client.process_image(
                receipt.image_data
            )
        except Exception as e:
            raise ExternalServiceError(
                service="OCR",
                message=f"OCR processing failed: {str(e)}",
                retryable=True
            )
        
        # Store result
        self._call_repository(
            self.repository.update,
            receipt_id,
            {"ocr_result": ocr_result}
        )
        
        self.logger.info(
            "Receipt OCR processed",
            extra={
                "receipt_id": receipt_id,
                "merchant": ocr_result.get("merchant"),
                "amount": ocr_result.get("amount"),
            }
        )
        
        return ocr_result
    
    def _validate_receipt(self, receipt_data: ReceiptUploadRequest) -> None:
        """Validate receipt data.
        
        Args:
            receipt_data: Receipt data to validate
            
        Raises:
            ValidationError: If invalid
        """
        errors = {}
        
        # Filename validation
        if not receipt_data.filename:
            errors["filename"] = "Filename required"
        
        # Image validation
        if not receipt_data.image_base64:
            errors["image_base64"] = "Image data required"
        
        # File size check (max 5MB)
        if receipt_data.image_base64:
            import base64
            try:
                decoded = base64.b64decode(receipt_data.image_base64)
                if len(decoded) > 5 * 1024 * 1024:
                    errors["image_base64"] = "Image too large (max 5MB)"
            except Exception:
                errors["image_base64"] = "Invalid base64 encoding"
        
        if errors:
            raise ValidationError(
                "Receipt validation failed",
                details=errors
            )
```

---

## 📊 AnalyticsService

### Implementation

```python
from datetime import datetime, timedelta
from typing import Dict, List
from app.services.base import CacheableService

class AnalyticsService(CacheableService):
    """Service for spending analytics.
    
    Handles:
    - Spending analysis and insights
    - Trend calculation
    - Budget tracking
    - Category analysis
    - Monthly comparisons
    """
    
    def __init__(self, logger, repository):
        """Initialize analytics service.
        
        Args:
            logger: Logger instance
            repository: AnalyticsRepository instance
        """
        super().__init__(logger, repository)
    
    def get_spending_insights(
        self,
        user_id: int,
        days: int = 30,
    ) -> Dict:
        """Get spending insights for period.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Insights dictionary
        """
        cache_key = f"insights:{user_id}:{days}"
        
        # Try cache
        cached = self.get_cached(cache_key)
        if cached:
            return cached
        
        self._log_operation(
            "Calculating spending insights",
            user_id=user_id,
            days=days,
        )
        
        # Calculate insights
        insights = self._call_repository(
            self.repository.get_insights,
            user_id, days
        )
        
        # Enhance with analysis
        insights.update({
            "average_daily": insights["total"] / days if days > 0 else 0,
            "trend": self._calculate_trend(user_id, days),
            "top_categories": self._get_top_categories(user_id, days),
        })
        
        # Cache
        self.set_cache(cache_key, insights, ttl=3600)
        
        return insights
    
    def get_category_breakdown(
        self,
        user_id: int,
        days: int = 30,
    ) -> Dict[str, float]:
        """Get spending by category.
        
        Args:
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Spending by category
        """
        self._log_operation(
            "Getting category breakdown",
            user_id=user_id,
            days=days,
        )
        
        breakdown = self._call_repository(
            self.repository.get_by_category_breakdown,
            user_id, days
        )
        
        return breakdown
    
    def get_budget_alerts(self, user_id: int) -> List[Dict]:
        """Get budget alerts for user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of budget alerts
        """
        self._log_operation(
            "Getting budget alerts",
            user_id=user_id,
        )
        
        alerts = self._call_repository(
            self.repository.get_budget_alerts,
            user_id
        )
        
        return alerts
    
    def _calculate_trend(
        self,
        user_id: int,
        days: int,
    ) -> str:
        """Calculate spending trend.
        
        Args:
            user_id: User ID
            days: Period to analyze
            
        Returns:
            "up", "down", or "stable"
        """
        first_half = days // 2
        second_half = days - first_half
        
        first = self._call_repository(
            self.repository.get_spending,
            user_id, second_half, first_half
        )
        second = self._call_repository(
            self.repository.get_spending,
            user_id, 0, second_half
        )
        
        if second > first * 1.1:
            return "up"
        elif second < first * 0.9:
            return "down"
        else:
            return "stable"
    
    def _get_top_categories(
        self,
        user_id: int,
        days: int,
        limit: int = 3,
    ) -> List[Dict]:
        """Get top spending categories.
        
        Args:
            user_id: User ID
            days: Period to analyze
            limit: Number of categories to return
            
        Returns:
            List of top categories with amounts
        """
        categories = self._call_repository(
            self.repository.get_by_category_breakdown,
            user_id, days
        )
        
        sorted_cats = sorted(
            categories.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {"category": cat, "amount": amount}
            for cat, amount in sorted_cats[:limit]
        ]
```

---

## 🧪 Testing Services

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, MagicMock
from app.services.expense import ExpenseService
from app.schemas.expense import ExpenseCreate
from app.core.exceptions import ValidationError, NotFoundError

@pytest.fixture
def mock_logger():
    return Mock()

@pytest.fixture
def mock_repository():
    return Mock()

@pytest.fixture
def service(mock_logger, mock_repository):
    return ExpenseService(mock_logger, mock_repository)

class TestExpenseService:
    
    def test_create_expense_success(self, service, mock_repository):
        """Test successful expense creation."""
        # Setup
        expense_data = ExpenseCreate(
            merchant="Coffee Shop",
            amount=5.50,
            category="Food",
        )
        mock_expense = Mock(id=1, merchant="Coffee Shop", amount=5.50)
        mock_repository.create.return_value = mock_expense
        
        # Execute
        result = service.create_expense(expense_data)
        
        # Verify
        assert result.id == 1
        mock_repository.create.assert_called_once()
    
    def test_create_expense_validation_error(self, service):
        """Test validation error on bad data."""
        # Setup
        expense_data = ExpenseCreate(
            merchant="",
            amount=-5.50,
            category="Invalid",
        )
        
        # Execute & Verify
        with pytest.raises(ValidationError):
            service.create_expense(expense_data)
    
    def test_get_expense_not_found(self, service, mock_repository):
        """Test not found error."""
        # Setup
        mock_repository.get_by_id.return_value = None
        
        # Execute & Verify
        with pytest.raises(NotFoundError):
            service.get_expense(999)
    
    def test_get_expense_success(self, service, mock_repository):
        """Test successful retrieval."""
        # Setup
        mock_expense = Mock(id=1, merchant="Shop")
        mock_repository.get_by_id.return_value = mock_expense
        
        # Execute
        result = service.get_expense(1)
        
        # Verify
        assert result.id == 1
```

---

## 🔄 Common Patterns

### Pattern: Validation + Execution

```python
def create(self, data):
    # Validate
    self._validate(data)
    
    # Execute
    result = self._call_repository(self.repo.create, data)
    
    # Post-process
    self._clear_cache()
    
    return result
```

### Pattern: Error Handling

```python
def process(self, id):
    try:
        return self._call_repository(self.repo.process, id)
    except RepositoryError as e:
        self.logger.error("Repository error", exc_info=True)
        raise DatabaseError(str(e))
    except Exception as e:
        self.logger.error("Unexpected error", exc_info=True)
        raise ExternalServiceError("Unknown", str(e))
```

### Pattern: Caching

```python
def get_expensive_operation(self, id):
    cache_key = f"expensive:{id}"
    
    cached = self.get_cached(cache_key)
    if cached:
        return cached
    
    result = self._call_repository(self.repo.compute, id)
    self.set_cache(cache_key, result, ttl=600)
    
    return result
```

### Pattern: Transactions

```python
def complex_operation(self, data):
    def logic():
        # Multiple operations that succeed together or fail together
        item1 = self._call_repository(self.repo.create, data1)
        item2 = self._call_repository(self.repo.create, data2)
        return {"item1": item1, "item2": item2}
    
    return self.execute_in_transaction(logic)
```

---

## 📚 Service Implementation Checklist

- [ ] Create ExpenseService (see above)
- [ ] Create ReceiptService (see above)
- [ ] Create AnalyticsService (see above)
- [ ] Create BudgetService (similar pattern)
- [ ] Implement all methods
- [ ] Add comprehensive validation
- [ ] Add error handling
- [ ] Add logging
- [ ] Create repositories for each service
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Document public methods
- [ ] Test with actual API

---

**Version:** 1.0.0  
**Status:** Ready for Implementation  
**Last Updated:** March 2024
