"""Insight service for spending analysis"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.core.logger import app_logger
from app.models import (
    SpendingSummary,
    CategoryInsight,
    SpendingTrend,
)
from app.database.repository import ExpenseRepository

try:
    from .llm_service import LLMService
except ImportError:
    LLMService = None


class InsightService:
    """Service for generating spending insights and recommendations"""

    def __init__(self, db: Session, llm_service = None):
        """Initialize insight service
        
        Args:
            db: Database session
            llm_service: LLM service instance (optional)
        """
        self.db = db
        self.repository = ExpenseRepository(db)
        self.llm_service = llm_service
        self.logger = app_logger

    def get_spending_summary(self, days: int = 30) -> SpendingSummary:
        """Get spending summary for specified period
        
        Args:
            days: Number of days to analyze
            
        Returns:
            SpendingSummary object
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            end_date = datetime.utcnow()
            
            self.logger.info(f"Generating spending summary for last {days} days")
            
            # Get spending by category
            category_data = self.repository.get_spending_by_category(start_date, end_date)
            
            # Get totals
            total_spending = self.repository.get_total_spending(start_date, end_date)
            transaction_count = self.repository.get_transaction_count(start_date, end_date)
            average_transaction = total_spending / transaction_count if transaction_count > 0 else 0
            
            # Create category insights
            categories = []
            highest_category = ""
            highest_amount = 0
            
            for item in category_data:
                insight = CategoryInsight(
                    category=item["category"],
                    total_amount=item["total"],
                    transaction_count=item["count"],
                    average_transaction=item["average"],
                    percentage_of_total=(item["total"] / total_spending * 100) if total_spending > 0 else 0,
                )
                categories.append(insight)
                
                if item["total"] > highest_amount:
                    highest_amount = item["total"]
                    highest_category = item["category"]
            
            # Sort categories by total amount
            categories.sort(key=lambda x: x.total_amount, reverse=True)
            
            summary = SpendingSummary(
                total_spending=total_spending,
                transaction_count=transaction_count,
                average_transaction=average_transaction,
                highest_category=highest_category or "N/A",
                period=f"Last {days} days",
                categories=categories,
            )
            
            self.logger.info(f"Generated summary: ${total_spending:.2f} spent in {transaction_count} transactions")
            
            return summary
        
        except Exception as e:
            self.logger.error(f"Failed to generate spending summary: {str(e)}")
            raise

    def get_spending_by_category(self, days: int = 30) -> List[CategoryInsight]:
        """Get spending breakdown by category
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of CategoryInsight
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        category_data = self.repository.get_spending_by_category(start_date, end_date)
        total_spending = self.repository.get_total_spending(start_date, end_date)
        
        insights = []
        for item in category_data:
            insight = CategoryInsight(
                category=item["category"],
                total_amount=item["total"],
                transaction_count=item["count"],
                average_transaction=item["average"],
                percentage_of_total=(item["total"] / total_spending * 100) if total_spending > 0 else 0,
            )
            insights.append(insight)
        
        # Sort by total amount
        insights.sort(key=lambda x: x.total_amount, reverse=True)
        
        return insights

    def get_monthly_insights(self, months: int = 3) -> dict:
        """Get monthly spending insights and recommendations
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary with monthly_data, trends, recommendations, budget_alerts
        """
        try:
            self.logger.info(f"Generating monthly insights for last {months} months")
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=months * 30)
            
            # Get all expenses in range
            expenses = self.repository.get_by_date_range(start_date, end_date)
            
            # Group expenses by month
            monthly_data = []
            months_dict = {}
            
            for expense in expenses:
                month_key = expense.date.strftime("%Y-%m")
                if month_key not in months_dict:
                    months_dict[month_key] = {
                        "total": 0,
                        "count": 0,
                        "categories": {}
                    }
                months_dict[month_key]["total"] += expense.amount
                months_dict[month_key]["count"] += 1
                
                cat = expense.category or "Other"
                if cat not in months_dict[month_key]["categories"]:
                    months_dict[month_key]["categories"][cat] = 0
                months_dict[month_key]["categories"][cat] += expense.amount
            
            # Convert to list format
            sorted_months = sorted(months_dict.keys())
            prev_total = 0
            
            for month in sorted_months:
                data = months_dict[month]
                days_in_month = 30
                
                # Calculate change from previous month
                change_amount = data["total"] - prev_total if prev_total > 0 else 0
                change_pct = (change_amount / prev_total * 100) if prev_total > 0 else 0
                
                # Get top categories
                top_cats = sorted(
                    data["categories"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                
                monthly_data.append({
                    "month": month,
                    "total_spending": round(data["total"], 2),
                    "transaction_count": data["count"],
                    "average_daily": round(data["total"] / days_in_month, 2),
                    "vs_previous_month": {
                        "change_amount": round(change_amount, 2),
                        "change_percentage": round(change_pct, 1),
                        "direction": "up" if change_amount > 0 else "down" if change_amount < 0 else "same"
                    },
                    "top_categories": [
                        {
                            "category": cat,
                            "amount": round(amt, 2),
                            "percentage": round(amt / data["total"] * 100, 1) if data["total"] > 0 else 0
                        }
                        for cat, amt in top_cats
                    ]
                })
                prev_total = data["total"]
            
            # Generate trends summary
            if len(monthly_data) >= 2:
                first_month = monthly_data[0]["total_spending"]
                last_month = monthly_data[-1]["total_spending"]
                overall_trend = "increasing" if last_month > first_month else "decreasing" if last_month < first_month else "stable"
            else:
                overall_trend = "insufficient_data"
            
            trends = {
                "overall_trend": overall_trend,
                "trend_description": f"Your spending is {overall_trend} over the past {months} months.",
                "spending_stability": 0.8
            }
            
            # Default recommendations
            recommendations = [
                {
                    "priority": "medium",
                    "category": "General",
                    "suggestion": "Track all expenses to identify spending patterns.",
                    "potential_savings": 50.0,
                    "savings_percentage": 5.0
                },
                {
                    "priority": "low",
                    "category": "Budgeting",
                    "suggestion": "Set monthly budgets for each spending category.",
                    "potential_savings": 100.0,
                    "savings_percentage": 10.0
                }
            ]
            
            # Budget alerts (empty for now, would require budget settings)
            budget_alerts = []
            
            self.logger.info(f"Generated monthly insights: {len(monthly_data)} months analyzed")
            
            return {
                "monthly_data": monthly_data,
                "trends": trends,
                "recommendations": recommendations,
                "budget_alerts": budget_alerts
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate monthly insights: {str(e)}")
            return {
                "monthly_data": [],
                "trends": {"overall_trend": "unknown", "trend_description": "Unable to analyze trends."},
                "recommendations": [],
                "budget_alerts": []
            }

    def get_spending_trends(self, days: int = 30) -> List[SpendingTrend]:
        """Get spending trends over time
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of SpendingTrend
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        expenses = self.repository.get_by_date_range(start_date, end_date)
        
        # Group by date
        trends_dict = {}
        for expense in expenses:
            date_key = expense.date.date()
            if date_key not in trends_dict:
                trends_dict[date_key] = 0
            trends_dict[date_key] += expense.amount
        
        # Convert to SpendingTrend objects
        trends = [
            SpendingTrend(date=datetime.combine(date, datetime.min.time()), amount=amount)
            for date, amount in sorted(trends_dict.items())
        ]
        
        return trends

    def get_recommendations(self, days: int = 30):
        """Generate cost-saving recommendations
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with suggestions and savings estimate
        """
        try:
            self.logger.info(f"Generating recommendations for last {days} days")
            
            # Get spending summary for context
            summary = self.get_spending_summary(days)
            
            # Create spending data string for LLM if service available
            if self.llm_service:
                spending_text = self._format_spending_for_llm(summary)
                recommendations = self.llm_service.generate_recommendations(spending_text)
            else:
                recommendations = []
            
            # Basic recommendations based on spending patterns
            suggestions = []
            total_savings = 0
            
            # Add default suggestions if no LLM recommendations
            if not recommendations:
                suggestions = [
                    {
                        "title": "Track your spending",
                        "description": "Keep detailed records of all expenses",
                        "potential_savings": 50.0,
                        "category": "General",
                        "priority": "high",
                    },
                    {
                        "title": "Set category budgets",
                        "description": "Allocate monthly budgets for each spending category",
                        "potential_savings": 100.0,
                        "category": "Budgeting",
                        "priority": "high",
                    },
                ]
                total_savings = 150.0
            else:
                for rec in recommendations:
                    suggestion = {
                        "title": rec.get("title", ""),
                        "description": rec.get("description", ""),
                        "potential_savings": float(rec.get("potential_savings", 0)),
                        "category": rec.get("category", "Other"),
                        "priority": rec.get("priority", "medium"),
                    }
                    suggestions.append(suggestion)
                    total_savings += suggestion["potential_savings"]
            
            self.logger.info(f"Generated {len(suggestions)} recommendations with ${total_savings:.2f} potential savings")
            
            return {
                "suggestions": suggestions,
                "total_potential_savings": total_savings,
                "analysis_period": f"Last {days} days",
            }
        
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {str(e)}")
            # Return empty response on failure
            return {
                "suggestions": [],
                "total_potential_savings": 0,
                "analysis_period": f"Last {days} days",
            }

    @staticmethod
    def _format_spending_for_llm(summary: SpendingSummary) -> str:
        """Format spending summary for LLM analysis
        
        Args:
            summary: SpendingSummary object
            
        Returns:
            Formatted text for LLM
        """
        text = f"""Spending Summary for {summary.period}:
Total Spending: ${summary.total_spending:.2f}
Number of Transactions: {summary.transaction_count}
Average Transaction: ${summary.average_transaction:.2f}
Highest Spending Category: {summary.highest_category}

Breakdown by Category:
"""
        
        for category in summary.categories:
            text += f"- {category.category}: ${category.total_amount:.2f} ({category.percentage_of_total:.1f}%) - {category.transaction_count} transactions\n"
        
        return text
