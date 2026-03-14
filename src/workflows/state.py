"""
FinSight AI Workflow State Schema

Defines the state objects used throughout the LangGraph workflow pipeline.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ExpenseItem:
    """Individual expense item extracted from receipt."""
    merchant: str
    amount: float
    category: Optional[str] = None
    confidence: float = 0.0
    description: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "merchant": self.merchant,
            "amount": self.amount,
            "category": self.category,
            "confidence": self.confidence,
            "description": self.description,
            "timestamp": self.timestamp
        }


@dataclass
class CategoryBreakdown:
    """Category-level spending statistics."""
    category: str
    amount: float
    count: int
    average: float = 0.0
    percentage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "amount": self.amount,
            "count": self.count,
            "average": self.average,
            "percentage": self.percentage
        }


@dataclass
class Recommendation:
    """Cost-saving recommendation."""
    title: str
    description: str
    category: str
    potential_savings: float
    priority: str  # HIGH, MEDIUM, LOW
    actionable_steps: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "potential_savings": self.potential_savings,
            "priority": self.priority,
            "actionable_steps": self.actionable_steps,
            "confidence": self.confidence
        }


@dataclass
class AnalysisResult:
    """Financial analysis result."""
    total_spending: float
    currency: str = "USD"
    category_breakdown: List[CategoryBreakdown] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)
    highest_spending_category: Optional[str] = None
    highest_spending_amount: float = 0.0
    expense_count: int = 0
    analysis_date: str = field(default_factory=lambda: datetime.now().isoformat())
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_spending": self.total_spending,
            "currency": self.currency,
            "category_breakdown": [cat.to_dict() for cat in self.category_breakdown],
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "highest_spending_category": self.highest_spending_category,
            "highest_spending_amount": self.highest_spending_amount,
            "expense_count": self.expense_count,
            "analysis_date": self.analysis_date,
            "summary": self.summary
        }


@dataclass
class WorkflowState:
    """
    Central state object for FinSight AI LangGraph workflow.
    
    This state flows through all nodes in the pipeline:
    1. OCR node → extracts text from image
    2. Expense extraction node → parses text into items
    3. Categorization node → assigns categories
    4. Database storage node → saves to database
    5. Financial analysis node → generates insights
    6. Recommendation node → creates recommendations
    """
    
    # Input
    input_type: str  # "text" or "image"
    input_content: str  # Text content or file path to image
    
    # OCR Output
    extracted_text: Optional[str] = None
    ocr_confidence: float = 0.0
    ocr_error: Optional[str] = None
    
    # Expense Extraction Output
    raw_items: List[ExpenseItem] = field(default_factory=list)
    extraction_error: Optional[str] = None
    
    # Categorization Output
    categorized_expenses: List[ExpenseItem] = field(default_factory=list)
    categorization_error: Optional[str] = None
    
    # Database Storage Output
    storage_id: Optional[str] = None
    storage_error: Optional[str] = None
    
    # Financial Analysis Output
    analysis: Optional[AnalysisResult] = None
    analysis_error: Optional[str] = None
    
    # Recommendations Output
    recommendations: List[Recommendation] = field(default_factory=list)
    recommendation_error: Optional[str] = None
    
    # Workflow metadata
    workflow_id: str = field(default_factory=lambda: datetime.now().isoformat())
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    workflow_error: Optional[str] = None
    processing_time_ms: float = 0.0
    
    # Configuration
    use_llm: bool = False
    budget_limits: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire workflow state to dictionary."""
        return {
            "input_type": self.input_type,
            "input_content": self.input_content,
            "extracted_text": self.extracted_text,
            "ocr_confidence": self.ocr_confidence,
            "raw_items": [item.to_dict() for item in self.raw_items],
            "categorized_expenses": [item.to_dict() for item in self.categorized_expenses],
            "storage_id": self.storage_id,
            "analysis": self.analysis.to_dict() if self.analysis else None,
            "recommendations": [rec.to_dict() for rec in self.recommendations],
            "workflow_id": self.workflow_id,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "processing_time_ms": self.processing_time_ms
        }
    
    def has_error(self) -> bool:
        """Check if any node encountered an error."""
        return any([
            self.ocr_error,
            self.extraction_error,
            self.categorization_error,
            self.storage_error,
            self.analysis_error,
            self.recommendation_error,
            self.workflow_error
        ])
    
    def get_errors(self) -> List[str]:
        """Get all errors encountered."""
        errors = []
        if self.ocr_error:
            errors.append(f"OCR Error: {self.ocr_error}")
        if self.extraction_error:
            errors.append(f"Extraction Error: {self.extraction_error}")
        if self.categorization_error:
            errors.append(f"Categorization Error: {self.categorization_error}")
        if self.storage_error:
            errors.append(f"Storage Error: {self.storage_error}")
        if self.analysis_error:
            errors.append(f"Analysis Error: {self.analysis_error}")
        if self.recommendation_error:
            errors.append(f"Recommendation Error: {self.recommendation_error}")
        if self.workflow_error:
            errors.append(f"Workflow Error: {self.workflow_error}")
        return errors
    
    def is_complete(self) -> bool:
        """Check if workflow completed successfully."""
        return (
            self.extracted_text is not None and
            len(self.categorized_expenses) > 0 and
            self.analysis is not None and
            not self.has_error()
        )
