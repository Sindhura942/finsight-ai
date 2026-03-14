"""API routes module

This module includes all API routes for FinSight AI:
- Receipt upload and analysis
- Expense management
- Spending insights and analytics
- Monthly reports and recommendations
- System health and statistics
"""

from fastapi import APIRouter

from .routes import router as main_router
from .expenses import router as expenses_router
from .insights import router as insights_router
from .health import router as health_router

# Create main router
router = APIRouter()

# Include comprehensive routes
router.include_router(main_router)

# Also include legacy routes for backward compatibility
router.include_router(health_router, prefix="/api/health", tags=["health"])
router.include_router(expenses_router, prefix="/api/expenses", tags=["expenses"])
router.include_router(insights_router, prefix="/api/insights", tags=["insights"])

__all__ = ["router"]
