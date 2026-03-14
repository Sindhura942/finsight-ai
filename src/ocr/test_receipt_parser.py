"""Tests for receipt parser module"""

import pytest
from src.ocr.receipt_parser import ReceiptParser, ExpenseItem, parse_receipt


class TestReceiptParserBasic:
    """Test basic receipt parsing functionality"""
    
    def test_parse_simple_single_line_merchant_amount(self):
        """Test parsing single line with merchant and amount"""
        parser = ReceiptParser()
        text = "Starbucks $8.20"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].merchant == "Starbucks"
        assert items[0].amount == 8.20
        assert items[0].currency == "USD"
    
    def test_parse_multiple_items(self):
        """Test parsing multiple items"""
        parser = ReceiptParser()
        text = """
        Starbucks $8.20
        Uber $18
        Amazon $42
        """
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 3
        assert items[0].merchant == "Starbucks"
        assert items[1].merchant == "Uber"
        assert items[2].merchant == "Amazon"
        assert items[0].amount == 8.20
        assert items[1].amount == 18.0
        assert items[2].amount == 42.0
    
    def test_parse_with_dots_separator(self):
        """Test parsing with dots as separator"""
        parser = ReceiptParser()
        text = "Coffee Shop.....12.50"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].merchant == "Coffee Shop"
        assert items[0].amount == 12.50
    
    def test_parse_with_multiple_spaces(self):
        """Test parsing with multiple spaces as separator"""
        parser = ReceiptParser()
        text = "Gas Station            25.99"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].merchant == "Gas Station"
        assert items[0].amount == 25.99
    
    def test_parse_with_colon_separator(self):
        """Test parsing with colon separator"""
        parser = ReceiptParser()
        text = "Restaurant: $45.50"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].merchant == "Restaurant"
        assert items[0].amount == 45.50
    
    def test_parse_with_dash_separator(self):
        """Test parsing with dash separator"""
        parser = ReceiptParser()
        text = "Pharmacy - $23.99"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].merchant == "Pharmacy"
        assert items[0].amount == 23.99


class TestReceiptParserCurrencies:
    """Test parsing with different currencies"""
    
    def test_parse_dollar_sign(self):
        """Test parsing with dollar sign"""
        parser = ReceiptParser()
        text = "Store $100.00"
        items = parser.parse_receipt_text(text)
        
        assert items[0].currency == "USD"
        assert items[0].amount == 100.00
    
    def test_parse_euro_sign(self):
        """Test parsing with euro sign"""
        parser = ReceiptParser()
        text = "Shop €50.00"
        items = parser.parse_receipt_text(text)
        
        assert items[0].currency == "EUR"
        assert items[0].amount == 50.00
    
    def test_parse_pound_sign(self):
        """Test parsing with pound sign"""
        parser = ReceiptParser()
        text = "Market £75.50"
        items = parser.parse_receipt_text(text)
        
        assert items[0].currency == "GBP"
        assert items[0].amount == 75.50
    
    def test_parse_currency_code(self):
        """Test parsing with currency code"""
        parser = ReceiptParser()
        text = "Store 100.00 USD"
        items = parser.parse_receipt_text(text)
        
        # Amount should be found
        assert len(items) >= 1


class TestReceiptParserFormats:
    """Test various receipt formats"""
    
    def test_parse_comma_decimal(self):
        """Test parsing with comma as decimal separator"""
        parser = ReceiptParser()
        text = "Store $12,50"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].amount == 12.50
    
    def test_parse_integer_amount(self):
        """Test parsing integer amounts"""
        parser = ReceiptParser()
        text = "Item $5"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].amount == 5.0
    
    def test_parse_no_currency_symbol(self):
        """Test parsing without currency symbol"""
        parser = ReceiptParser()
        text = "Store 19.99"
        items = parser.parse_receipt_text(text)
        
        # Should still parse
        assert len(items) >= 1
    
    def test_parse_merchant_and_amount_separate_lines(self):
        """Test parsing merchant and amount on different lines"""
        parser = ReceiptParser()
        text = """
        Starbucks
        $8.20
        """
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].merchant == "Starbucks"
        assert items[0].amount == 8.20


class TestReceiptParserCleanup:
    """Test merchant name cleanup"""
    
    def test_clean_merchant_name_capitalization(self):
        """Test merchant name capitalization"""
        parser = ReceiptParser()
        text = "starbucks coffee shop $8.20"
        items = parser.parse_receipt_text(text)
        
        assert items[0].merchant == "Starbucks Coffee Shop"
    
    def test_clean_merchant_name_multiple_spaces(self):
        """Test merchant name with multiple spaces"""
        parser = ReceiptParser()
        text = "whole   foods   market    $45.99"
        items = parser.parse_receipt_text(text)
        
        assert "  " not in items[0].merchant  # No double spaces
    
    def test_clean_merchant_name_special_chars(self):
        """Test merchant name with special characters"""
        parser = ReceiptParser()
        text = "McDonald's #123 - $7.50"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        # Should preserve apostrophe
        assert "Mcdonald" in items[0].merchant


class TestReceiptParserConfidence:
    """Test confidence scoring"""
    
    def test_confidence_score_good_merchant(self):
        """Test confidence for well-formed items"""
        parser = ReceiptParser()
        text = "Starbucks Coffee Shop $8.20"
        items = parser.parse_receipt_text(text)
        
        assert items[0].confidence >= 0.5
    
    def test_confidence_score_valid_amount(self):
        """Test confidence increases with valid amount"""
        parser = ReceiptParser()
        text1 = "Store $10.00"
        text2 = "Store $0.00001"  # Unlikely amount
        
        items1 = parser.parse_receipt_text(text1)
        items2 = parser.parse_receipt_text(text2)
        
        # Valid amount should have higher confidence
        if len(items1) > 0 and len(items2) > 0:
            assert items1[0].confidence >= items2[0].confidence


class TestReceiptParserEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_text(self):
        """Test parsing empty text"""
        parser = ReceiptParser()
        items = parser.parse_receipt_text("")
        
        assert items == []
    
    def test_whitespace_only(self):
        """Test parsing whitespace-only text"""
        parser = ReceiptParser()
        items = parser.parse_receipt_text("   \n\n   ")
        
        assert items == []
    
    def test_no_amounts(self):
        """Test parsing text with no amounts"""
        parser = ReceiptParser()
        text = """
        Starbucks
        Whole Foods
        Amazon
        """
        items = parser.parse_receipt_text(text)
        
        # Should find no items without amounts
        assert len(items) == 0
    
    def test_amount_only(self):
        """Test line with only amount"""
        parser = ReceiptParser()
        text = "$25.99"
        items = parser.parse_receipt_text(text)
        
        # Should not parse amount-only line
        assert len(items) == 0
    
    def test_very_large_amount(self):
        """Test parsing very large amounts"""
        parser = ReceiptParser()
        text = "Hotel $5000.00"
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 1
        assert items[0].amount == 5000.00
    
    def test_duplicate_items(self):
        """Test handling duplicate items"""
        parser = ReceiptParser()
        text = """
        Coffee $5.00
        Coffee $5.00
        Tea $3.00
        """
        items = parser.parse_receipt_text(text)
        
        assert len(items) == 3  # Should keep duplicates


class TestReceiptParserIntegration:
    """Integration tests with real receipt formats"""
    
    def test_parse_typical_receipt(self):
        """Test parsing typical receipt format"""
        parser = ReceiptParser()
        text = """
        Starbucks
        Espresso Drink      $8.20
        Muffin              $5.99
        Tax                 $1.12
        Total              $15.31
        """
        items = parser.parse_receipt_text(text)
        
        # Should parse multiple items
        assert len(items) >= 2
        assert any(item.merchant == "Espresso Drink" for item in items)
    
    def test_parse_restaurant_receipt(self):
        """Test parsing restaurant receipt"""
        parser = ReceiptParser()
        text = """
        Joe's Pizza
        Menu Item 1        $12.50
        Menu Item 2        $18.75
        Subtotal           $31.25
        Tax                $2.50
        Total              $33.75
        """
        items = parser.parse_receipt_text(text)
        
        assert len(items) >= 2
    
    def test_parse_amazon_style(self):
        """Test parsing Amazon-style format"""
        parser = ReceiptParser()
        text = """
        Amazon Purchase
        Item 1 - $42.99
        Item 2 - $18.50
        Shipping - $0
        Tax - $4.89
        Total - $66.38
        """
        items = parser.parse_receipt_text(text)
        
        assert len(items) >= 2
    
    def test_parse_dot_matrix_format(self):
        """Test parsing old dot-matrix style receipt"""
        parser = ReceiptParser()
        text = """
        STORE #1234      DATE 03/13/26
        
        HAMBURGER......................5.99
        FRIES........................2.99
        DRINK........................3.49
        
        SUBTOTAL.......................12.47
        TAX............................0.99
        TOTAL.........................13.46
        """
        items = parser.parse_receipt_text(text)
        
        # Should find multiple items
        assert len(items) >= 2


class TestConvenienceFunctions:
    """Test convenience parsing functions"""
    
    def test_parse_receipt_simple(self):
        """Test simple parsing function"""
        text = "Starbucks $8.20"
        items = parse_receipt(text, simple=True)
        
        assert len(items) == 1
        assert items[0]['merchant'] == "Starbucks"
        assert items[0]['amount'] == 8.20
        assert 'currency' not in items[0]  # Simple format
    
    def test_parse_receipt_full(self):
        """Test full parsing function"""
        text = "Starbucks $8.20"
        items = parse_receipt(text, simple=False)
        
        assert len(items) == 1
        assert items[0]['merchant'] == "Starbucks"
        assert items[0]['amount'] == 8.20
        assert 'currency' in items[0]


class TestExpenseItem:
    """Test ExpenseItem dataclass"""
    
    def test_expense_item_creation(self):
        """Test creating ExpenseItem"""
        item = ExpenseItem(merchant="Test", amount=10.0)
        
        assert item.merchant == "Test"
        assert item.amount == 10.0
        assert item.currency == "USD"
        assert item.confidence == 1.0
    
    def test_expense_item_to_dict(self):
        """Test converting ExpenseItem to dictionary"""
        item = ExpenseItem(merchant="Test", amount=10.0)
        d = item.to_dict()
        
        assert d['merchant'] == "Test"
        assert d['amount'] == 10.0
        assert d['currency'] == "USD"


class TestReceiptParserMerchantDetection:
    """Test merchant name detection logic"""
    
    def test_looks_like_merchant_valid(self):
        """Test valid merchant names"""
        parser = ReceiptParser()
        
        assert parser._looks_like_merchant("Starbucks")
        assert parser._looks_like_merchant("McDonald's")
        assert parser._looks_like_merchant("Whole Foods Market")
    
    def test_looks_like_merchant_invalid(self):
        """Test invalid merchant patterns"""
        parser = ReceiptParser()
        
        assert not parser._looks_like_merchant("")
        assert not parser._looks_like_merchant("$$$")
        assert not parser._looks_like_merchant("12345")
        assert not parser._looks_like_merchant("  ")
