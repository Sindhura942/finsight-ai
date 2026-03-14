"""AI Agents module for FinSight AI"""

from .llm_agent import LLMAgent
from .categorizer import CategorizerAgent as CategorizerAgentOld
from .categorizer_agent import CategorizerAgent, CategorizedExpense, categorize_expenses
from .analyzer import AnalyzerAgent
from .recommender import RecommenderAgent
from .financial_analyzer import (
    FinancialAnalyzer,
    FinancialAnalysis,
    CategoryBreakdown,
    CostSavingRecommendation,
    analyze_expenses as analyze_expenses_financial
)

__all__ = [
    "LLMAgent",
    "CategorizerAgent",
    "CategorizedExpense",
    "categorize_expenses",
    "AnalyzerAgent",
    "RecommenderAgent",
    "FinancialAnalyzer",
    "FinancialAnalysis",
    "CategoryBreakdown",
    "CostSavingRecommendation",
    "analyze_expenses_financial",
]
