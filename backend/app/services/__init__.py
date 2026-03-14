"""Services module initialization"""

from .expense_service import ExpenseService
from .insight_service import InsightService

# Optional services - only import if dependencies are available
try:
    from .ocr_service import OCRService
except ImportError:
    OCRService = None

try:
    from .llm_service import LLMService
except ImportError:
    LLMService = None

__all__ = ["ExpenseService", "InsightService", "OCRService", "LLMService"]
