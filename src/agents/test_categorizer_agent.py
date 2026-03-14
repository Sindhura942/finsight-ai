"""Tests for expense categorizer agent"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from src.agents.categorizer_agent import (
    CategorizerAgent,
    CategorizedExpense,
    categorize_expenses
)


class TestCategorizedExpense:
    """Test CategorizedExpense dataclass"""
    
    def test_create_categorized_expense(self):
        """Test creating CategorizedExpense"""
        expense = CategorizedExpense(
            merchant="Starbucks",
            amount=8.0,
            category="food"
        )
        
        assert expense.merchant == "Starbucks"
        assert expense.amount == 8.0
        assert expense.category == "food"
        assert expense.currency == "USD"
        assert expense.confidence == 1.0
    
    def test_categorized_expense_to_dict(self):
        """Test converting to dictionary"""
        expense = CategorizedExpense(
            merchant="Starbucks",
            amount=8.0,
            category="food",
            confidence=0.95,
            reasoning="Food & beverage"
        )
        
        d = expense.to_dict()
        assert d['merchant'] == "Starbucks"
        assert d['amount'] == 8.0
        assert d['category'] == "food"
        assert d['confidence'] == 0.95


class TestCategorizerAgentKeywordFallback:
    """Test keyword-based fallback categorization"""
    
    def test_categorize_starbucks_keyword(self):
        """Test Starbucks categorization using keywords"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "Starbucks", "amount": 8.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.merchant == "Starbucks"
        assert result.amount == 8.0
        assert result.category == "food"
    
    def test_categorize_uber_keyword(self):
        """Test Uber categorization using keywords"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "Uber", "amount": 18.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.category == "transport"
    
    def test_categorize_amazon_keyword(self):
        """Test Amazon categorization using keywords"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "Amazon", "amount": 42.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.category == "shopping"
    
    def test_categorize_whole_foods_keyword(self):
        """Test Whole Foods categorization using keywords"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "Whole Foods Market", "amount": 50.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.category == "groceries"
    
    def test_categorize_unknown_merchant_keyword(self):
        """Test unknown merchant defaults to other"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "Unknown Store XYZ", "amount": 25.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.category == "other"
        assert result.confidence < 0.7
    
    def test_case_insensitive_matching(self):
        """Test keyword matching is case insensitive"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "STARBUCKS COFFEE", "amount": 8.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.category == "food"


class TestCategorizerAgentPromptBuilding:
    """Test prompt building for LLM"""
    
    def test_build_single_prompt(self):
        """Test single expense prompt building"""
        agent = CategorizerAgent()
        
        expense = {"merchant": "Starbucks", "amount": 8.0}
        prompt = agent._build_single_prompt(expense)
        
        assert "Starbucks" in prompt
        assert "8" in prompt
        assert "food" in prompt
        assert "JSON" in prompt
    
    def test_build_batch_prompt(self):
        """Test batch expenses prompt building"""
        agent = CategorizerAgent()
        
        expenses = [
            {"merchant": "Starbucks", "amount": 8.0},
            {"merchant": "Uber", "amount": 18.0}
        ]
        prompt = agent._build_batch_prompt(expenses)
        
        assert "Starbucks" in prompt
        assert "Uber" in prompt
        assert "food" in prompt
        assert "transport" in prompt
        assert "JSON" in prompt
        assert "[]" in prompt  # Should mention array


class TestCategorizerAgentJsonExtraction:
    """Test JSON extraction from responses"""
    
    def test_extract_json_plain(self):
        """Test extracting plain JSON"""
        agent = CategorizerAgent()
        
        json_str = '{"category": "food", "confidence": 0.95}'
        result = agent._extract_json(json_str)
        
        assert result is not None
        data = json.loads(result)
        assert data['category'] == "food"
    
    def test_extract_json_markdown_code_block(self):
        """Test extracting JSON from markdown code block"""
        agent = CategorizerAgent()
        
        response = """Here's the result:
```json
{"category": "food", "confidence": 0.95}
```
Done!"""
        result = agent._extract_json(response)
        
        assert result is not None
        data = json.loads(result)
        assert data['category'] == "food"
    
    def test_extract_json_array(self):
        """Test extracting JSON array"""
        agent = CategorizerAgent()
        
        response = """Result:
[
  {"category": "food", "confidence": 0.95},
  {"category": "transport", "confidence": 0.90}
]"""
        result = agent._extract_json(response)
        
        assert result is not None
        data = json.loads(result)
        assert len(data) == 2
        assert data[0]['category'] == "food"
    
    def test_extract_json_object(self):
        """Test extracting JSON object from text"""
        agent = CategorizerAgent()
        
        response = """Some text before
{"category": "food", "confidence": 0.95}
Some text after"""
        result = agent._extract_json(response)
        
        assert result is not None
        data = json.loads(result)
        assert data['category'] == "food"
    
    def test_extract_json_invalid_returns_none(self):
        """Test that invalid JSON returns None"""
        agent = CategorizerAgent()
        
        response = "This is not JSON at all"
        result = agent._extract_json(response)
        
        assert result is None


class TestCategorizerAgentResponseParsing:
    """Test parsing LLM responses"""
    
    def test_parse_single_response(self):
        """Test parsing single expense response"""
        agent = CategorizerAgent()
        
        response = '{"category": "food", "confidence": 0.95, "reasoning": "Food place"}'
        expense = {"merchant": "Starbucks", "amount": 8.0}
        
        result = agent._parse_single_response(response, expense)
        
        assert result is not None
        assert result.category == "food"
        assert result.confidence == 0.95
        assert result.reasoning == "Food place"
    
    def test_parse_single_response_invalid_category(self):
        """Test parsing with invalid category defaults to other"""
        agent = CategorizerAgent()
        
        response = '{"category": "invalid_cat", "confidence": 0.95}'
        expense = {"merchant": "Store", "amount": 10.0}
        
        result = agent._parse_single_response(response, expense)
        
        assert result is not None
        assert result.category == "other"
    
    def test_parse_single_response_invalid_json(self):
        """Test parsing invalid JSON returns None"""
        agent = CategorizerAgent()
        
        response = "This is not JSON"
        expense = {"merchant": "Store", "amount": 10.0}
        
        result = agent._parse_single_response(response, expense)
        
        assert result is None
    
    def test_parse_batch_response(self):
        """Test parsing batch response"""
        agent = CategorizerAgent()
        
        response = '''[
            {"category": "food", "confidence": 0.95, "reasoning": "Coffee"},
            {"category": "transport", "confidence": 0.90, "reasoning": "Ride"}
        ]'''
        expenses = [
            {"merchant": "Starbucks", "amount": 8.0},
            {"merchant": "Uber", "amount": 18.0}
        ]
        
        result = agent._parse_batch_response(response, expenses)
        
        assert result is not None
        assert len(result) == 2
        assert result[0].category == "food"
        assert result[1].category == "transport"
    
    def test_parse_batch_response_not_array(self):
        """Test parsing non-array response returns None"""
        agent = CategorizerAgent()
        
        response = '{"category": "food"}'
        expenses = [{"merchant": "Store", "amount": 10.0}]
        
        result = agent._parse_batch_response(response, expenses)
        
        assert result is None


class TestCategorizerAgentCategories:
    """Test category management"""
    
    def test_get_categories(self):
        """Test getting category list"""
        agent = CategorizerAgent()
        
        categories = agent.get_categories()
        
        assert "food" in categories
        assert "transport" in categories
        assert "shopping" in categories
        assert len(categories) > 0
    
    def test_add_category(self):
        """Test adding new category"""
        agent = CategorizerAgent()
        
        agent.add_category("pet", ["vet", "pet store", "dog", "cat"])
        
        assert "pet" in agent.CATEGORIES
        assert "pet" in agent.CATEGORY_KEYWORDS
    
    def test_add_duplicate_category(self):
        """Test adding duplicate category is ignored"""
        agent = CategorizerAgent()
        
        original_keywords = len(agent.CATEGORY_KEYWORDS.get("food", []))
        agent.add_category("food", ["pizza"])
        
        # Should not have changed
        assert len(agent.CATEGORY_KEYWORDS["food"]) == original_keywords


class TestCategorizerAgentIntegration:
    """Integration tests for categorizer agent"""
    
    def test_categorize_expenses_without_llm(self):
        """Test categorizing expenses using keyword fallback"""
        agent = CategorizerAgent(use_fallback=True)
        
        expenses = [
            {"merchant": "Starbucks", "amount": 8.0},
            {"merchant": "Uber", "amount": 18.0},
            {"merchant": "Amazon", "amount": 42.0}
        ]
        
        result = agent.categorize_expenses(expenses, use_llm=False)
        
        assert len(result) == 3
        assert result[0].category == "food"
        assert result[1].category == "transport"
        assert result[2].category == "shopping"
    
    def test_categorize_empty_list(self):
        """Test categorizing empty list"""
        agent = CategorizerAgent(use_fallback=True)
        
        result = agent.categorize_expenses([], use_llm=False)
        
        assert result == []
    
    def test_categorize_expenses_fallback_on_error(self):
        """Test fallback to keyword when LLM fails"""
        agent = CategorizerAgent(use_fallback=True)
        
        expenses = [
            {"merchant": "Starbucks", "amount": 8.0}
        ]
        
        # Even without LLM, should work with keyword fallback
        result = agent.categorize_expenses(expenses, use_llm=False)
        
        assert len(result) == 1
        assert result[0].category == "food"


class TestConvenienceFunction:
    """Test convenience function"""
    
    def test_categorize_expenses_function(self):
        """Test convenience categorize_expenses function"""
        expenses = [
            {"merchant": "Starbucks", "amount": 8.0},
            {"merchant": "Uber", "amount": 18.0}
        ]
        
        result = categorize_expenses(expenses, use_llm=False)
        
        assert len(result) == 2
        assert result[0]['category'] == "food"
        assert result[1]['category'] == "transport"
        assert result[0]['merchant'] == "Starbucks"
        assert result[0]['amount'] == 8.0


class TestCategorizerAgentAvailability:
    """Test Ollama availability checking"""
    
    def test_ollama_availability_cached(self):
        """Test that availability check is cached"""
        agent = CategorizerAgent()
        
        # First check
        result1 = agent._is_ollama_available()
        # Second check should use cache
        result2 = agent._is_ollama_available()
        
        # Should be same result (from cache)
        assert result1 == result2
    
    @patch('httpx.get')
    def test_ollama_available_true(self, mock_get):
        """Test when Ollama is available"""
        agent = CategorizerAgent()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = agent._is_ollama_available()
        
        assert result is True
    
    @patch('httpx.get')
    def test_ollama_available_false(self, mock_get):
        """Test when Ollama is not available"""
        agent = CategorizerAgent()
        
        mock_get.side_effect = Exception("Connection failed")
        
        result = agent._is_ollama_available()
        
        assert result is False


class TestCategorizerAgentConfiguration:
    """Test agent configuration"""
    
    def test_custom_ollama_host(self):
        """Test custom Ollama host"""
        agent = CategorizerAgent(ollama_host="http://example.com:11434")
        
        assert agent.ollama_host == "http://example.com:11434"
    
    def test_custom_model(self):
        """Test custom model selection"""
        agent = CategorizerAgent(model="llama2")
        
        assert agent.model == "llama2"
    
    def test_custom_timeout(self):
        """Test custom timeout"""
        agent = CategorizerAgent(timeout=60)
        
        assert agent.timeout == 60
    
    def test_disable_fallback(self):
        """Test disabling fallback"""
        agent = CategorizerAgent(use_fallback=False)
        
        assert agent.use_fallback is False


class TestCategorizerAgentEdgeCases:
    """Test edge cases"""
    
    def test_missing_merchant_field(self):
        """Test handling expense without merchant field"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"amount": 10.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.merchant == "Unknown"
    
    def test_missing_amount_field(self):
        """Test handling expense without amount field"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "Starbucks"}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.amount == 0
    
    def test_negative_amount(self):
        """Test handling negative amounts"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "Starbucks", "amount": -8.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.amount == -8.0
    
    def test_very_large_amount(self):
        """Test handling very large amounts"""
        agent = CategorizerAgent(use_fallback=True)
        
        expense = {"merchant": "Hotel", "amount": 5000.0}
        result = agent._categorize_single_keyword(expense)
        
        assert result is not None
        assert result.amount == 5000.0
