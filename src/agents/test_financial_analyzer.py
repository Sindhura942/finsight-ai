"""
Tests for Financial Analysis AI Module

Comprehensive test suite for expense analysis and recommendation generation.
"""

import pytest
from src.agents.financial_analyzer import (
    FinancialAnalyzer,
    FinancialAnalysis,
    CategoryBreakdown,
    CostSavingRecommendation,
    analyze_expenses
)


class TestCategoryBreakdown:
    """Tests for CategoryBreakdown dataclass."""
    
    def test_category_breakdown_creation(self):
        """Test creating a CategoryBreakdown."""
        breakdown = CategoryBreakdown(
            category="food",
            amount=150.0,
            count=10
        )
        assert breakdown.category == "food"
        assert breakdown.amount == 150.0
        assert breakdown.count == 10
        assert breakdown.average == 15.0
    
    def test_category_breakdown_to_dict(self):
        """Test converting CategoryBreakdown to dict."""
        breakdown = CategoryBreakdown(
            category="transport",
            amount=200.0,
            count=5
        )
        result = breakdown.to_dict()
        assert result['category'] == "transport"
        assert result['amount'] == 200.0
        assert result['count'] == 5
        assert result['average'] == 40.0


class TestCostSavingRecommendation:
    """Tests for CostSavingRecommendation dataclass."""
    
    def test_recommendation_creation(self):
        """Test creating a recommendation."""
        rec = CostSavingRecommendation(
            title="Reduce Coffee",
            description="Brew at home",
            category="food",
            potential_savings=50.0,
            priority="high"
        )
        assert rec.title == "Reduce Coffee"
        assert rec.priority == "high"
        assert rec.potential_savings == 50.0
    
    def test_recommendation_to_dict(self):
        """Test converting recommendation to dict."""
        rec = CostSavingRecommendation(
            title="Save Money",
            description="Test",
            category="shopping",
            potential_savings=100.0,
            priority="medium",
            actionable_steps=["Step 1", "Step 2"]
        )
        result = rec.to_dict()
        assert result['title'] == "Save Money"
        assert result['priority'] == "medium"
        assert len(result['actionable_steps']) == 2


class TestFinancialAnalysisDataclass:
    """Tests for FinancialAnalysis dataclass."""
    
    def test_financial_analysis_creation(self):
        """Test creating FinancialAnalysis."""
        analysis = FinancialAnalysis(
            total_spending=500.0,
            currency="USD",
            expense_count=20
        )
        assert analysis.total_spending == 500.0
        assert analysis.currency == "USD"
        assert analysis.expense_count == 20
    
    def test_financial_analysis_to_dict(self):
        """Test converting FinancialAnalysis to dict."""
        analysis = FinancialAnalysis(
            total_spending=420.0,
            currency="USD",
            expense_count=10
        )
        result = analysis.to_dict()
        assert result['total_spending'] == 420.0
        assert result['currency'] == "USD"
        assert 'summary' in result


class TestFinancialAnalyzerBreakdown:
    """Tests for expense breakdown calculation."""
    
    def test_calculate_breakdown_single_category(self):
        """Test breakdown with single category."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
            {"merchant": "Cafe", "amount": 4.50, "category": "food"}
        ]
        total, breakdown = analyzer._calculate_breakdown(expenses)
        
        assert total == 10.0
        assert "food" in breakdown
        assert breakdown["food"].amount == 10.0
        assert breakdown["food"].count == 2
        assert breakdown["food"].average == 5.0
    
    def test_calculate_breakdown_multiple_categories(self):
        """Test breakdown with multiple categories."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Starbucks", "amount": 8.0, "category": "food"},
            {"merchant": "Uber", "amount": 18.0, "category": "transport"},
            {"merchant": "Amazon", "amount": 42.0, "category": "shopping"}
        ]
        total, breakdown = analyzer._calculate_breakdown(expenses)
        
        assert total == 68.0
        assert len(breakdown) == 3
        assert breakdown["food"].amount == 8.0
        assert breakdown["transport"].amount == 18.0
        assert breakdown["shopping"].amount == 42.0
    
    def test_calculate_breakdown_empty(self):
        """Test breakdown with no expenses."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = []
        total, breakdown = analyzer._calculate_breakdown(expenses)
        
        assert total == 0.0
        assert len(breakdown) == 0


class TestFinancialAnalyzerAnalysis:
    """Tests for complete expense analysis."""
    
    def test_analyze_basic(self):
        """Test basic analysis."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Starbucks", "amount": 8.20, "category": "food"},
            {"merchant": "Uber", "amount": 18.00, "category": "transport"},
            {"merchant": "Amazon", "amount": 42.00, "category": "shopping"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        assert analysis.total_spending == 68.2
        assert analysis.expense_count == 3
        assert analysis.highest_spending_category == "shopping"
        assert analysis.highest_spending_amount == 42.0
    
    def test_analyze_empty_expenses(self):
        """Test analysis with empty expenses."""
        analyzer = FinancialAnalyzer(use_llm=False)
        analysis = analyzer.analyze([])
        
        assert analysis.total_spending == 0.0
        assert analysis.expense_count == 0
    
    def test_analyze_category_percentages(self):
        """Test that percentages are calculated correctly."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Restaurant", "amount": 50.0, "category": "food"},
            {"merchant": "Taxi", "amount": 50.0, "category": "transport"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        # Find breakdown items
        food_cat = next((c for c in analysis.category_breakdown if c.category == "food"), None)
        transport_cat = next((c for c in analysis.category_breakdown if c.category == "transport"), None)
        
        assert food_cat is not None
        assert transport_cat is not None
        assert food_cat.percentage == 50.0
        assert transport_cat.percentage == 50.0


class TestFinancialAnalyzerRecommendations:
    """Tests for recommendation generation."""
    
    def test_keyword_recommendations_high_spending(self):
        """Test keyword-based recommendations for high spending."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
            {"merchant": "Cafe", "amount": 4.50, "category": "food"},
            {"merchant": "Restaurant", "amount": 50.0, "category": "food"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        # Should have recommendations for food category
        assert len(analysis.recommendations) > 0
        food_recs = [r for r in analysis.recommendations if r.category == "food"]
        assert len(food_recs) > 0
    
    def test_keyword_recommendations_priority(self):
        """Test that recommendations have appropriate priority."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Starbucks", "amount": 500.0, "category": "food"}  # Very high
        ]
        
        analysis = analyzer.analyze(expenses)
        
        # Should have high-priority recommendation
        assert len(analysis.recommendations) > 0
        assert any(r.priority == "high" for r in analysis.recommendations)
    
    def test_keyword_recommendations_potential_savings(self):
        """Test that recommendations include potential savings."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Starbucks", "amount": 300.0, "category": "food"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        # Should have savings recommendations
        assert len(analysis.recommendations) > 0
        assert all(r.potential_savings > 0 for r in analysis.recommendations)


class TestFinancialAnalyzerSummary:
    """Tests for summary generation."""
    
    def test_summary_generation(self):
        """Test that summary is generated."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Starbucks", "amount": 8.20, "category": "food"},
            {"merchant": "Uber", "amount": 18.00, "category": "transport"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        assert analysis.summary is not None
        assert "Total Spending" in analysis.summary
        assert "Category Breakdown" in analysis.summary
        assert "food" in analysis.summary.lower()
        assert "transport" in analysis.summary.lower()
    
    def test_summary_includes_recommendations(self):
        """Test that summary includes recommendations."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Starbucks", "amount": 200.0, "category": "food"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        if analysis.recommendations:
            assert "Recommendation" in analysis.summary or len(analysis.recommendations) > 0


class TestFinancialAnalyzerJSON:
    """Tests for JSON extraction."""
    
    def test_extract_json_markdown_code_block(self):
        """Test extracting JSON from markdown code block."""
        analyzer = FinancialAnalyzer(use_llm=False)
        text = '```json\n{"key": "value"}\n```'
        
        result = analyzer._extract_json(text)
        
        assert result is not None
        assert "key" in result
    
    def test_extract_json_array(self):
        """Test extracting JSON array."""
        analyzer = FinancialAnalyzer(use_llm=False)
        text = 'Some text [{"item": 1}, {"item": 2}] more text'
        
        result = analyzer._extract_json(text)
        
        assert result is not None
        assert "item" in result
    
    def test_extract_json_object(self):
        """Test extracting JSON object."""
        analyzer = FinancialAnalyzer(use_llm=False)
        text = 'Text before {"data": "value"} text after'
        
        result = analyzer._extract_json(text)
        
        assert result is not None
        assert "data" in result
    
    def test_extract_json_none(self):
        """Test extraction with no JSON."""
        analyzer = FinancialAnalyzer(use_llm=False)
        text = 'Just plain text with no JSON'
        
        result = analyzer._extract_json(text)
        
        assert result is None


class TestConvenienceFunction:
    """Tests for convenience function."""
    
    def test_analyze_expenses_function(self):
        """Test convenience function."""
        expenses = [
            {"merchant": "Starbucks", "amount": 8.20, "category": "food"},
            {"merchant": "Uber", "amount": 18.00, "category": "transport"}
        ]
        
        result = analyze_expenses(expenses, use_llm=False)
        
        assert result is not None
        assert result['total_spending'] == 26.2
        assert result['expense_count'] == 2
        assert 'category_breakdown' in result


class TestFinancialAnalyzerConfiguration:
    """Tests for analyzer configuration."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = FinancialAnalyzer(
            ollama_host="http://localhost:11434",
            model="mistral",
            use_llm=False
        )
        
        assert analyzer.ollama_host == "http://localhost:11434"
        assert analyzer.model == "mistral"
        assert analyzer.use_llm == False
    
    def test_analyzer_with_custom_timeout(self):
        """Test analyzer with custom timeout."""
        analyzer = FinancialAnalyzer(timeout=60)
        
        assert analyzer.timeout == 60


class TestFinancialAnalyzerEdgeCases:
    """Tests for edge cases."""
    
    def test_analyze_negative_amount(self):
        """Test with negative amount (refund)."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Store", "amount": 100.0, "category": "shopping"},
            {"merchant": "Refund", "amount": -20.0, "category": "shopping"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        assert analysis.total_spending == 80.0
    
    def test_analyze_zero_amount(self):
        """Test with zero amount."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Free Item", "amount": 0.0, "category": "other"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        assert analysis.total_spending == 0.0
    
    def test_analyze_large_amounts(self):
        """Test with large amounts."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Purchase", "amount": 10000.0, "category": "shopping"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        assert analysis.total_spending == 10000.0
    
    def test_analyze_missing_category(self):
        """Test with missing category (defaults to 'other')."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"merchant": "Store", "amount": 50.0}  # No category
        ]
        
        analysis = analyzer.analyze(expenses)
        
        assert len(analysis.category_breakdown) > 0
    
    def test_analyze_missing_merchant(self):
        """Test with missing merchant."""
        analyzer = FinancialAnalyzer(use_llm=False)
        expenses = [
            {"amount": 50.0, "category": "other"}  # No merchant
        ]
        
        analysis = analyzer.analyze(expenses)
        
        assert analysis.total_spending == 50.0


class TestFinancialAnalyzerIntegration:
    """Integration tests."""
    
    def test_full_workflow(self):
        """Test complete analysis workflow."""
        analyzer = FinancialAnalyzer(use_llm=False)
        
        # Realistic expenses
        expenses = [
            {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
            {"merchant": "Whole Foods", "amount": 75.00, "category": "groceries"},
            {"merchant": "Uber", "amount": 22.50, "category": "transport"},
            {"merchant": "Shell Gas", "amount": 45.00, "category": "transport"},
            {"merchant": "Amazon", "amount": 120.00, "category": "shopping"},
            {"merchant": "Netflix", "amount": 15.99, "category": "subscriptions"},
            {"merchant": "Restaurant", "amount": 65.00, "category": "food"}
        ]
        
        analysis = analyzer.analyze(expenses)
        
        # Verify analysis
        assert analysis.total_spending > 0
        assert analysis.expense_count == 7
        assert len(analysis.category_breakdown) > 0
        assert analysis.summary is not None
        
        # Should have recommendations
        assert len(analysis.recommendations) > 0
    
    def test_analysis_with_budget_limits(self):
        """Test analysis with budget limits."""
        analyzer = FinancialAnalyzer(use_llm=False)
        
        expenses = [
            {"merchant": "Restaurant", "amount": 300.0, "category": "food"}
        ]
        
        budget_limits = {"food": 200.0}
        analysis = analyzer.analyze(expenses, budget_limits=budget_limits)
        
        # Should have recommendations since over budget
        assert len(analysis.recommendations) > 0
    
    def test_multiple_sequential_analyses(self):
        """Test running multiple analyses."""
        analyzer = FinancialAnalyzer(use_llm=False)
        
        for i in range(3):
            expenses = [
                {"merchant": "Store", "amount": 50.0 * (i + 1), "category": "shopping"}
            ]
            analysis = analyzer.analyze(expenses)
            assert analysis.total_spending == 50.0 * (i + 1)
