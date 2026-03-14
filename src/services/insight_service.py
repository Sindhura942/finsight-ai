"""Insight service for analytics"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from src.database.repository import ExpenseRepository
from src.agents import AnalyzerAgent, RecommenderAgent
from src.schemas import SpendingSummary, CategoryInsight, RecommendationsResponse
from src.utils import get_logger

logger = get_logger("InsightService")


class InsightService:
    """Service for spending insights and analytics"""

    def __init__(self, db: Session):
        """Initialize insight service
        
        Args:
            db: Database session
        """
        self.db = db
        self.repository = ExpenseRepository(db)
        self.analyzer = AnalyzerAgent()
        self.recommender = RecommenderAgent()

    def get_spending_summary(self, days: int = 30) -> SpendingSummary:
        """Get spending summary
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Spending summary
        """
        try:
            logger.info(f"Generating summary for {days} days")
            
            start_date = datetime.utcnow() - timedelta(days=days)
            end_date = datetime.utcnow()
            
            # Get spending by category
            category_data = self.repository.get_spending_by_category(start_date, end_date)
            
            # Get totals
            total = self.repository.get_total_spending(start_date, end_date)
            count = self.repository.get_transaction_count(start_date, end_date)
            average = total / count if count > 0 else 0
            
            # Build category insights
            categories = []
            highest_category = ""
            highest_amount = 0
            
            for item in category_data:
                insight = CategoryInsight(
                    category=item["category"],
                    total_amount=item["total"],
                    transaction_count=item["count"],
                    average_transaction=item["average"],
                    percentage_of_total=(item["total"] / total * 100) if total > 0 else 0,
                )
                categories.append(insight)
                
                if item["total"] > highest_amount:
                    highest_amount = item["total"]
                    highest_category = item["category"]
            
            # Sort by amount
            categories.sort(key=lambda x: x.total_amount, reverse=True)
            
            return SpendingSummary(
                total_spending=total,
                transaction_count=count,
                average_transaction=average,
                highest_category=highest_category or "N/A",
                period=f"Last {days} days",
                categories=categories,
            )
        
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            raise

    def get_recommendations(self, days: int = 30) -> RecommendationsResponse:
        """Get cost-saving recommendations
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Recommendations response
        """
        try:
            logger.info(f"Generating recommendations for {days} days")
            
            summary = self.get_spending_summary(days)
            
            # Format for LLM
            spending_text = self._format_spending_for_analysis(summary)
            
            # Generate recommendations
            recommendations = self.recommender.generate_recommendations(spending_text)
            
            # Calculate total savings
            total_savings = sum(r.get("potential_savings", 0) for r in recommendations)
            
            return RecommendationsResponse(
                suggestions=[],  # Convert to schema objects
                total_potential_savings=total_savings,
                analysis_period=f"Last {days} days",
            )
        
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            raise

    @staticmethod
    def _format_spending_for_analysis(summary: SpendingSummary) -> str:
        """Format spending for analysis
        
        Args:
            summary: Spending summary
            
        Returns:
            Formatted text
        """
        text = f"""Spending Summary for {summary.period}:
Total Spending: ${summary.total_spending:.2f}
Transactions: {summary.transaction_count}
Average: ${summary.average_transaction:.2f}
Highest: {summary.highest_category}

Breakdown:
"""
        
        for cat in summary.categories:
            text += f"- {cat.category}: ${cat.total_amount:.2f} ({cat.percentage_of_total:.1f}%)\n"
        
        return text
