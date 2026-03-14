"""
LangGraph Workflow Tests

Comprehensive test suite for FinSight AI LangGraph workflow.
"""

import unittest
import json
import sqlite3
from datetime import datetime
from src.workflows import (
    FinSightWorkflow,
    WorkflowState,
    ExpenseItem,
    Recommendation,
    AnalysisResult,
    CategoryBreakdown
)


class TestWorkflowState(unittest.TestCase):
    """Test WorkflowState dataclass"""
    
    def test_state_creation(self):
        """Test creating a workflow state"""
        state = WorkflowState(
            input_type="text",
            input_content="Test content"
        )
        self.assertEqual(state.input_type, "text")
        self.assertEqual(state.input_content, "Test content")
    
    def test_state_to_dict(self):
        """Test converting state to dictionary"""
        state = WorkflowState(
            input_type="text",
            input_content="Test"
        )
        state_dict = state.to_dict()
        self.assertIsInstance(state_dict, dict)
        self.assertEqual(state_dict["input_type"], "text")
    
    def test_error_tracking(self):
        """Test error tracking methods"""
        state = WorkflowState(
            input_type="text",
            input_content="Test"
        )
        self.assertFalse(state.has_error())
        
        state.ocr_error = "Test error"
        self.assertTrue(state.has_error())
        self.assertEqual(len(state.get_errors()), 1)
    
    def test_completion_status(self):
        """Test completion status check"""
        state = WorkflowState(
            input_type="text",
            input_content="Test"
        )
        self.assertFalse(state.is_complete())
        
        state.extracted_text = "Extracted"
        state.categorized_expenses = [ExpenseItem(merchant="Test", amount=10.0)]
        state.analysis = AnalysisResult(total_spending=10.0)
        self.assertTrue(state.is_complete())


class TestExpenseItem(unittest.TestCase):
    """Test ExpenseItem dataclass"""
    
    def test_item_creation(self):
        """Test creating an expense item"""
        item = ExpenseItem(
            merchant="Starbucks",
            amount=6.50,
            category="food",
            confidence=0.95
        )
        self.assertEqual(item.merchant, "Starbucks")
        self.assertEqual(item.amount, 6.50)
        self.assertEqual(item.category, "food")
    
    def test_item_to_dict(self):
        """Test converting item to dictionary"""
        item = ExpenseItem(merchant="Test", amount=10.0)
        item_dict = item.to_dict()
        self.assertEqual(item_dict["merchant"], "Test")
        self.assertEqual(item_dict["amount"], 10.0)


class TestRecommendation(unittest.TestCase):
    """Test Recommendation dataclass"""
    
    def test_recommendation_creation(self):
        """Test creating a recommendation"""
        rec = Recommendation(
            title="Reduce Coffee",
            description="Buy less coffee",
            category="food",
            potential_savings=50.0,
            priority="HIGH",
            confidence=0.85
        )
        self.assertEqual(rec.title, "Reduce Coffee")
        self.assertEqual(rec.priority, "HIGH")
    
    def test_recommendation_with_steps(self):
        """Test recommendation with actionable steps"""
        rec = Recommendation(
            title="Test",
            description="Test desc",
            category="food",
            potential_savings=10.0,
            priority="MEDIUM",
            actionable_steps=["Step 1", "Step 2"]
        )
        self.assertEqual(len(rec.actionable_steps), 2)


class TestAnalysisResult(unittest.TestCase):
    """Test AnalysisResult dataclass"""
    
    def test_analysis_creation(self):
        """Test creating analysis result"""
        analysis = AnalysisResult(total_spending=100.0)
        self.assertEqual(analysis.total_spending, 100.0)
        self.assertEqual(analysis.currency, "USD")
    
    def test_analysis_with_breakdown(self):
        """Test analysis with category breakdown"""
        analysis = AnalysisResult(
            total_spending=100.0,
            category_breakdown=[
                CategoryBreakdown(category="food", amount=50.0, count=5),
                CategoryBreakdown(category="transport", amount=50.0, count=2)
            ]
        )
        self.assertEqual(len(analysis.category_breakdown), 2)
    
    def test_analysis_to_dict(self):
        """Test converting analysis to dictionary"""
        analysis = AnalysisResult(
            total_spending=100.0,
            category_breakdown=[
                CategoryBreakdown(category="food", amount=50.0, count=5)
            ]
        )
        analysis_dict = analysis.to_dict()
        self.assertEqual(analysis_dict["total_spending"], 100.0)
        self.assertEqual(len(analysis_dict["category_breakdown"]), 1)


class TestFinSightWorkflow(unittest.TestCase):
    """Test FinSightWorkflow"""
    
    def setUp(self):
        """Set up test workflow with in-memory database"""
        self.workflow = FinSightWorkflow(
            use_llm=False,
            db_path=":memory:"
        )
    
    def test_workflow_initialization(self):
        """Test workflow initialization"""
        self.assertIsNotNone(self.workflow.ocr)
        self.assertIsNotNone(self.workflow.parser)
        self.assertIsNotNone(self.workflow.categorizer)
        self.assertIsNotNone(self.workflow.analyzer)
    
    def test_workflow_text_input(self):
        """Test workflow with text input"""
        result = self.workflow.run(
            input_type="text",
            input_content="Starbucks $6.50"
        )
        
        self.assertIsNotNone(result.extracted_text)
        self.assertEqual(result.extracted_text, "Starbucks $6.50")
        self.assertEqual(result.ocr_confidence, 1.0)
    
    def test_workflow_empty_input(self):
        """Test workflow with empty input"""
        result = self.workflow.run(
            input_type="text",
            input_content=""
        )
        
        self.assertTrue(result.has_error())
        self.assertIsNotNone(result.ocr_error)
    
    def test_workflow_complete_text(self):
        """Test complete workflow with full text"""
        receipt_text = """
        Starbucks
        Latte - $6.50
        Croissant - $4.20
        
        Whole Foods
        Milk - $5.99
        Bread - $4.50
        """
        
        result = self.workflow.run(
            input_type="text",
            input_content=receipt_text
        )
        
        # Check extraction
        self.assertIsNotNone(result.extracted_text)
        
        # Check parsing
        self.assertGreater(len(result.raw_items), 0)
        
        # Check categorization
        self.assertGreater(len(result.categorized_expenses), 0)
        
        # Check analysis
        self.assertIsNotNone(result.analysis)
        self.assertGreater(result.analysis.total_spending, 0)
    
    def test_workflow_with_budget(self):
        """Test workflow with budget limits"""
        result = self.workflow.run(
            input_type="text",
            input_content="Coffee $10.00",
            budget_limits={"food": 5.0}
        )
        
        self.assertEqual(result.budget_limits["food"], 5.0)
    
    def test_workflow_metadata(self):
        """Test workflow metadata"""
        result = self.workflow.run(
            input_type="text",
            input_content="Starbucks $6.50"
        )
        
        self.assertIsNotNone(result.workflow_id)
        self.assertIsNotNone(result.created_at)
        self.assertIsNotNone(result.completed_at)
        self.assertGreater(result.processing_time_ms, 0)
    
    def test_workflow_state_flow(self):
        """Test that state flows through all nodes"""
        result = self.workflow.run(
            input_type="text",
            input_content="Test $10.00"
        )
        
        # Check each node produced output
        self.assertIsNotNone(result.extracted_text)  # OCR node
        self.assertIsNotNone(result.raw_items)  # Extraction node
        self.assertIsNotNone(result.categorized_expenses)  # Categorization node
        self.assertIsNotNone(result.storage_id)  # Storage node
        self.assertIsNotNone(result.analysis)  # Analysis node
        self.assertIsNotNone(result.recommendations)  # Recommendations node
    
    def test_workflow_error_propagation(self):
        """Test error propagation through workflow"""
        result = self.workflow.run(
            input_type="invalid",
            input_content="test"
        )
        
        self.assertTrue(result.has_error())
        errors = result.get_errors()
        self.assertGreater(len(errors), 0)
    
    def test_database_storage(self):
        """Test that workflow stores data in database"""
        # Create workflow with file database
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name
        
        try:
            workflow = FinSightWorkflow(use_llm=False, db_path=db_path)
            result = workflow.run(
                input_type="text",
                input_content="Test $10.00"
            )
            
            # Check database was created and contains data
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM receipts")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0)
            
            conn.close()
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)


class TestWorkflowIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""
    
    def setUp(self):
        """Set up test workflow"""
        self.workflow = FinSightWorkflow(
            use_llm=False,
            db_path=":memory:"
        )
    
    def test_multiple_receipts(self):
        """Test processing multiple receipts"""
        receipts = [
            "Starbucks $6.50",
            "Whole Foods $25.00",
            "Uber $18.75"
        ]
        
        total = 0
        for receipt in receipts:
            result = self.workflow.run(
                input_type="text",
                input_content=receipt
            )
            if result.analysis:
                total += result.analysis.total_spending
        
        self.assertGreater(total, 0)
    
    def test_json_serialization(self):
        """Test JSON serialization of results"""
        result = self.workflow.run(
            input_type="text",
            input_content="Test $10.00"
        )
        
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict, default=str)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        self.assertIsNotNone(parsed)
    
    def test_workflow_recovery(self):
        """Test workflow graceful error recovery"""
        # First request fails
        result1 = self.workflow.run(
            input_type="text",
            input_content=""
        )
        self.assertTrue(result1.has_error())
        
        # Second request succeeds
        result2 = self.workflow.run(
            input_type="text",
            input_content="Starbucks $6.50"
        )
        self.assertFalse(result2.has_error())


class TestWorkflowPerformance(unittest.TestCase):
    """Performance tests"""
    
    def setUp(self):
        """Set up test workflow"""
        self.workflow = FinSightWorkflow(
            use_llm=False,
            db_path=":memory:"
        )
    
    def test_single_receipt_performance(self):
        """Test single receipt processing time"""
        result = self.workflow.run(
            input_type="text",
            input_content="Starbucks $6.50"
        )
        
        # Should complete in reasonable time
        self.assertLess(result.processing_time_ms, 2000)  # 2 seconds
    
    def test_large_receipt_performance(self):
        """Test large receipt processing time"""
        # Create a large receipt with many items
        items = "\n".join([f"Item {i}: ${10 + i}.00" for i in range(50)])
        
        result = self.workflow.run(
            input_type="text",
            input_content=items
        )
        
        # Should still complete in reasonable time
        self.assertLess(result.processing_time_ms, 5000)  # 5 seconds


if __name__ == "__main__":
    unittest.main()
