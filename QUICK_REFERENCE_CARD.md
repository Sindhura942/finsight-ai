# Quick Reference Card - Production Refactoring

**FinSight AI v2.0.0** | Print or bookmark this page

---

## 📍 Start Here

```bash
# 1. Understand the architecture
PRODUCTION_REFACTORING_GUIDE.md

# 2. Implement services
SERVICE_IMPLEMENTATION_GUIDE.md

# 3. Write tests
TESTING_GUIDE.md

# 4. Deploy
DEPLOYMENT_GUIDE.md
```

---

## 🏗️ Architecture Layers

| Layer | Purpose | Example |
|-------|---------|---------|
| **Route** | API endpoint | `POST /api/expenses` |
| **DTO** | Validation | `ExpenseCreate` schema |
| **Middleware** | Logging, errors, CORS | `LoggingMiddleware` |
| **Service** | Business logic | `ExpenseService.create()` |
| **Repository** | Data access | `ExpenseRepository.save()` |
| **Database** | Persistence | SQLAlchemy model |

---

## 📦 Module Checklist

| Module | File | Status | Lines |
|--------|------|--------|-------|
| Exceptions | `core/exceptions.py` | ✅ | 200+ |
| Services | `services/base.py` | ✅ | 200+ |
| Repositories | `repositories/base.py` | ✅ | 200+ |
| Schemas | `schemas/expense.py` | ✅ | 300+ |
| Middleware | `middleware/http.py` | ✅ | 300+ |
| Config | `core/config_v2.py` | ✅ | 200+ |

---

## 🎯 Exception Classes

```python
from app.core.exceptions import (
    ValidationError,       # 400
    NotFoundError,         # 404
    BusinessLogicError,    # 400
    DatabaseError,         # 500
    ExternalServiceError,  # 503
    AuthenticationError,   # 401
    AuthorizationError,    # 403
    RateLimitError,        # 429
)

# Usage
raise ValidationError("Invalid", details={"field": "value"})
```

---

## 🔧 Service Pattern

```python
from app.services.base import BaseService

class MyService(BaseService):
    def create(self, data):
        # Log
        self._log_operation("Creating", data=data)
        
        # Validate (add custom validation)
        self._validate(data)
        
        # Call repository safely
        result = self._call_repository(
            self.repository.create,
            data
        )
        
        # Clear cache
        self.clear_cache("summary:*")
        
        return result
    
    def get_cached(self, key):
        # Check cache
        cached = self.get_cached(key)
        if cached:
            return cached
        
        # Calculate
        result = expensive_operation()
        
        # Cache
        self.set_cache(key, result, ttl=600)
        
        return result
```

---

## 📝 Repository Pattern

```python
from app.repositories.base import BaseRepository

class MyRepository(BaseRepository):
    model = MyModel
    
    # CRUD automatic
    # create(), get_by_id(), get_all(), update(), delete()
    
    # Add custom queries
    def get_by_category(self, category):
        return self.query().filter(
            self.model.category == category
        ).all()
```

---

## ✅ DTO/Schema Pattern

```python
from pydantic import BaseModel, Field, validator

class MyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Name required")
        return v.strip()

class MyResponse(BaseModel):
    id: int
    name: str
    amount: float
    
    class Config:
        from_attributes = True  # For ORM models
```

---

## 🚀 API Endpoint Pattern

```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/items", tags=["items"])

# Dependencies
def get_service() -> MyService:
    logger = get_logger(__name__)
    repo = MyRepository(db)
    return MyService(logger, repo)

# Endpoints
@router.post("/", response_model=MyResponse)
async def create(
    data: MyCreate,
    service: MyService = Depends(get_service),
):
    return service.create(data)

@router.get("/{id}", response_model=MyResponse)
async def get(
    id: int,
    service: MyService = Depends(get_service),
):
    return service.get(id)

@router.put("/{id}", response_model=MyResponse)
async def update(
    id: int,
    data: MyUpdate,
    service: MyService = Depends(get_service),
):
    return service.update(id, data)

@router.delete("/{id}")
async def delete(
    id: int,
    service: MyService = Depends(get_service),
):
    service.delete(id)
    return {"status": "deleted"}
```

---

## 🧪 Unit Test Pattern

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_repo():
    return Mock()

@pytest.fixture
def service(mock_repo):
    return MyService(Mock(), mock_repo)

def test_create_success(service, mock_repo):
    # Setup
    mock_repo.create.return_value = Mock(id=1)
    
    # Execute
    result = service.create(valid_data)
    
    # Verify
    assert result.id == 1
    mock_repo.create.assert_called_once()

def test_create_validation_error(service):
    # Execute & Verify
    with pytest.raises(ValidationError):
        service.create(invalid_data)
```

---

## 🔍 Configuration Pattern

```python
from app.core.config import settings

# Access settings
settings.api_host          # "0.0.0.0"
settings.api_port          # 8000
settings.database_url      # From environment
settings.log_level         # "INFO"
settings.is_production     # Computed property

# Environment variable mapping
# DATABASE_URL → settings.database_url
# LOG_LEVEL → settings.log_level
# ENVIRONMENT → settings.environment
```

---

## 📊 Common Configurations

```env
# .env.development
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///dev.db
DEBUG=true

# .env.production
ENVIRONMENT=production
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pwd@host/db
DEBUG=false
```

---

## 🎯 Logging Pattern

```python
from app.core.logger import get_logger

logger = get_logger(__name__)

# Simple logging
logger.info("Operation started")

# Structured logging
logger.info(
    "Expense created",
    extra={
        "expense_id": 123,
        "amount": 50.00,
        "category": "Food",
    }
)

# Error logging
logger.error(
    "Operation failed",
    exc_info=True,
    extra={"operation": "create_expense"}
)
```

---

## 🚦 HTTP Status Codes

| Code | Exception | Usage |
|------|-----------|-------|
| 400 | ValidationError | Invalid input |
| 401 | AuthenticationError | Not authenticated |
| 403 | AuthorizationError | Not authorized |
| 404 | NotFoundError | Resource not found |
| 429 | RateLimitError | Too many requests |
| 500 | DatabaseError | DB failure |
| 503 | ExternalServiceError | External API down |

---

## 🔒 Security Checklist

- [ ] HTTPS enforced
- [ ] CORS configured
- [ ] Input validated (Pydantic)
- [ ] Errors don't leak details
- [ ] SQL injection prevented (ORM)
- [ ] Rate limiting enabled
- [ ] Secrets in environment
- [ ] Logging doesn't log secrets
- [ ] JWT tokens configured
- [ ] CSRF protection enabled

---

## 📈 Testing Checklist

- [ ] Unit tests: >90% coverage
- [ ] Integration tests: >85% coverage
- [ ] E2E tests: >80% coverage
- [ ] Service tests pass
- [ ] Repository tests pass
- [ ] Schema tests pass
- [ ] Endpoint tests pass
- [ ] Error handling tested
- [ ] Edge cases covered
- [ ] Performance acceptable

---

## 🚀 Deployment Checklist

- [ ] Tests passing
- [ ] Code reviewed
- [ ] Security scan passed
- [ ] Database migrations ready
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] Alerting configured
- [ ] Runbooks prepared
- [ ] Team notified
- [ ] Rollback plan ready

---

## 📞 Quick Links

| Task | Document |
|------|----------|
| Understand architecture | `PRODUCTION_REFACTORING_GUIDE.md` |
| Implement services | `SERVICE_IMPLEMENTATION_GUIDE.md` |
| Write tests | `TESTING_GUIDE.md` |
| Deploy | `DEPLOYMENT_GUIDE.md` |
| Project overview | `PRODUCTION_REFACTORING_SUMMARY.md` |
| Getting started | `README_REFACTORING.md` |

---

## 🎯 Implementation Order

1. **Review Architecture** (30 min)
   - Read PRODUCTION_REFACTORING_GUIDE.md
   - Understand layers
   - Review examples

2. **Implement Services** (2-3 days)
   - Follow SERVICE_IMPLEMENTATION_GUIDE.md
   - Create ExpenseService
   - Create ReceiptService
   - Create AnalyticsService

3. **Refactor Endpoints** (2-3 days)
   - Update routes to use services
   - Add DTOs for validation
   - Update error handling

4. **Write Tests** (2-3 days)
   - Follow TESTING_GUIDE.md
   - Unit tests (>90%)
   - Integration tests
   - E2E tests

5. **Deploy** (1-2 days)
   - Follow DEPLOYMENT_GUIDE.md
   - Environment setup
   - Deploy to staging
   - Deploy to production

---

## 💡 Pro Tips

✅ Copy service pattern, adapt for your domain  
✅ Use decorators for caching: `@cache(expire=300)`  
✅ Always log operations with context  
✅ Use type hints for IDE support  
✅ Mock repositories in unit tests  
✅ Test error cases, not just happy path  
✅ Use database transactions for consistency  
✅ Cache expensive operations  
✅ Monitor in production  
✅ Document your decisions  

---

## 🔗 File Locations

```
backend/app/
├── core/
│   ├── exceptions.py          ← Exception classes
│   ├── config_v2.py           ← Settings management
│   └── logger.py              ← Logging setup
├── services/
│   ├── base.py                ← Base service classes
│   └── [your_services.py]     ← Implement here
├── repositories/
│   ├── base.py                ← Base repository
│   └── [your_repos.py]        ← Implement here
├── schemas/
│   ├── expense.py             ← DTOs for expenses
│   └── [your_schemas.py]      ← Add more DTOs
├── middleware/
│   └── http.py                ← Middleware stack
└── api/
    └── routes/
        ├── expenses.py        ← Expense endpoints
        ├── receipts.py        ← Receipt endpoints
        └── budgets.py         ← Budget endpoints
```

---

## 🎓 Learning Resources

**Provided in Project:**
- 4 comprehensive guides
- 60+ code examples
- 40+ test examples
- Architecture diagrams
- Best practices
- Implementation checklists

**External Resources:**
- FastAPI docs: https://fastapi.tiangolo.com
- Pydantic docs: https://docs.pydantic.dev
- SQLAlchemy docs: https://docs.sqlalchemy.org
- pytest docs: https://docs.pytest.org

---

## ✨ Key Takeaways

1. **Layered Architecture** - Each layer has one responsibility
2. **Dependency Injection** - Easier to test and maintain
3. **Exception Handling** - Custom exceptions for consistency
4. **Data Validation** - Pydantic handles it automatically
5. **Logging** - Structured logs for debugging
6. **Testing** - Unit, integration, E2E tests
7. **Documentation** - Code is self-documenting with docstrings

---

**Print this card and keep it handy!**

---

**Version:** 2.0.0  
**Status:** Production Ready ✅  
**Last Updated:** March 2024

**Happy coding!** 🚀
