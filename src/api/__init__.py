"""API module with route handlers"""

from .expenses import router as expenses_router
from .insights import router as insights_router
from .health import router as health_router

__all__ = [
    "expenses_router",
    "insights_router",
    "health_router",
]
