"""Receipt text parser for extracting structured expense data"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal, InvalidOperation

from src.utils import get_logger

logger = get_logger("ReceiptParser")


@dataclass
class ExpenseItem:
    """Structured expense data from receipt"""
    merchant: str
    amount: float
    category: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    currency: str = "USD"
    confidence: float = 1.0
    raw_text: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class ReceiptParser:
    """Parser for converting receipt OCR text into structured expense data"""
    
    # Common currency symbols and patterns
    CURRENCY_PATTERNS = {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        'USD': 'USD',
        'EUR': 'EUR',
        'GBP': 'GBP',
        'JPY': 'JPY',
    }
    
    # Patterns for common merchant names (to identify merchant lines)
    MERCHANT_INDICATORS = {
        'store', 'shop', 'market', 'coffee', 'restaurant', 'cafe',
        'grocery', 'pharmacy', 'gas', 'fuel', 'hotel', 'airline',
        'uber', 'lyft', 'taxi', 'amazon', 'ebay', 'walmart',
        'target', 'costco', 'bestbuy', 'home depot', 'lowe',
        'starbucks', 'mcdonald', 'burger', 'pizza', 'subway',
        'whole foods', 'trader joe', 'safeway', 'kroger', 'publix'
    }
    
    # Amount patterns
    AMOUNT_PATTERN = r'[\$€£]?\s*(\d+[.,]\d{2}|\d+)'
    AMOUNT_PATTERN_VERBOSE = r'(?:^|\s)([\$€£]?)\s*(\d+[.,]\d{1,2})\s*(?:$|\s)'
    
    # Common separator patterns between merchant and amount
    SEPARATOR_PATTERNS = [
        r'\.{2,}',  # dots: Store Name.....5.99
        r'\s{2,}',  # multiple spaces: Store Name     5.99
        r'\t+',     # tabs
        r':\s*',    # colon: Store Name: 5.99
        r'-\s*',    # dash: Store Name - 5.99
    ]
    
    def __init__(self, strict_mode: bool = False):
        """Initialize receipt parser
        
        Args:
            strict_mode: If True, requires high confidence matches only
        """
        self.strict_mode = strict_mode
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance"""
        self.amount_regex = re.compile(self.AMOUNT_PATTERN_VERBOSE, re.IGNORECASE)
        self.separator_regexes = [re.compile(pattern) for pattern in self.SEPARATOR_PATTERNS]
        self.merchant_indicator_regex = re.compile(
            '|'.join(self.MERCHANT_INDICATORS),
            re.IGNORECASE
        )
    
    def parse_receipt_text(self, text: str) -> List[ExpenseItem]:
        """Parse receipt OCR text into structured expense data
        
        Args:
            text: Multi-line receipt text from OCR
            
        Returns:
            List of ExpenseItem objects with parsed data
            
        Example:
            >>> text = '''
            ... Starbucks
            ... Coffee           $8.20
            ... Uber
            ... Ride             $18.00
            ... '''
            >>> parser = ReceiptParser()
            >>> items = parser.parse_receipt_text(text)
            >>> items[0].merchant
            'Starbucks'
            >>> items[0].amount
            8.2
        """
        if not text or not text.strip():
            logger.warning("Empty receipt text provided")
            return []
        
        expenses = []
        lines = text.strip().split('\n')
        
        # First pass: try to find merchant-amount pairs on same line
        remaining_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to parse as merchant + amount on single line
            item = self._parse_single_line(line)
            if item:
                expenses.append(item)
            else:
                remaining_lines.append(line)
        
        # Second pass: try to pair merchants with amounts from adjacent lines
        if remaining_lines:
            paired_items = self._pair_merchants_with_amounts(remaining_lines)
            expenses.extend(paired_items)
        
        # Sort by confidence descending
        expenses.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.info(f"Parsed {len(expenses)} expense items from receipt")
        return expenses
    
    def _parse_single_line(self, line: str) -> Optional[ExpenseItem]:
        """Parse a single line that may contain merchant and amount
        
        Args:
            line: Single line of receipt text
            
        Returns:
            ExpenseItem if successful, None otherwise
        """
        # Try to find amount in line
        amount_match = self.amount_regex.search(line)
        if not amount_match:
            return None
        
        currency_symbol = amount_match.group(1) or '$'
        amount_str = amount_match.group(2)
        
        try:
            # Normalize decimal separator
            amount_str = amount_str.replace(',', '.')
            amount = float(amount_str)
        except ValueError:
            return None
        
        # Extract merchant name (everything before amount)
        amount_start = amount_match.start()
        merchant = line[:amount_start].strip()
        
        # Clean merchant name
        merchant = self._clean_merchant_name(merchant)
        if not merchant:
            return None
        
        # Determine currency
        currency = self.CURRENCY_PATTERNS.get(currency_symbol, 'USD')
        
        # Calculate confidence
        confidence = self._calculate_confidence(merchant, amount, line)
        
        return ExpenseItem(
            merchant=merchant,
            amount=amount,
            currency=currency,
            confidence=confidence,
            raw_text=line
        )
    
    def _pair_merchants_with_amounts(self, lines: List[str]) -> List[ExpenseItem]:
        """Pair merchant names with amounts from different lines
        
        Args:
            lines: List of remaining lines after single-line parsing
            
        Returns:
            List of ExpenseItem objects
        """
        items = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line looks like a merchant name
            if self._looks_like_merchant(line):
                merchant = self._clean_merchant_name(line)
                
                # Look for amount in next few lines
                found = False
                for j in range(i + 1, min(i + 3, len(lines))):  # Check next 2 lines
                    next_line = lines[j]
                    amount_match = self.amount_regex.search(next_line)
                    
                    if amount_match:
                        currency_symbol = amount_match.group(1) or '$'
                        amount_str = amount_match.group(2)
                        
                        try:
                            amount_str = amount_str.replace(',', '.')
                            amount = float(amount_str)
                            
                            currency = self.CURRENCY_PATTERNS.get(currency_symbol, 'USD')
                            confidence = self._calculate_confidence(merchant, amount, line)
                            
                            items.append(ExpenseItem(
                                merchant=merchant,
                                amount=amount,
                                currency=currency,
                                confidence=confidence,
                                raw_text=f"{line} | {next_line}"
                            ))
                            
                            i = j  # Skip to the line with amount
                            found = True
                            break
                        except ValueError:
                            continue
                
                if not found:
                    i += 1
            else:
                i += 1
        
        return items
    
    def _clean_merchant_name(self, text: str) -> str:
        """Clean and normalize merchant name
        
        Args:
            text: Raw merchant name text
            
        Returns:
            Cleaned merchant name
        """
        if not text:
            return ""
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove common prefixes/suffixes
        text = re.sub(r'^(transaction|receipt|merchant):\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\s*(store|location|branch)$', '', text, flags=re.IGNORECASE)
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters except spaces
        text = re.sub(r'[^\w\s&\'-]', '', text)
        
        # Capitalize first letter of each word
        text = ' '.join(word.capitalize() for word in text.split())
        
        return text.strip()
    
    def _looks_like_merchant(self, text: str) -> bool:
        """Determine if text looks like a merchant name
        
        Args:
            text: Text to check
            
        Returns:
            True if text appears to be a merchant name
        """
        if not text or len(text) < 2:
            return False
        
        # Should not contain only amounts
        if re.match(r'^[\$€£\d.,\s]+$', text):
            return False
        
        # Should start with a letter
        if not re.match(r'^[a-zA-Z]', text):
            return False
        
        # Should not be too long (typical merchant names are shorter)
        if len(text) > 100:
            return False
        
        # Optionally check for merchant indicators
        # if self.merchant_indicator_regex.search(text):
        #     return True
        
        # If it looks vaguely merchant-like, accept it
        return len(text) > 2 and text[0].isalpha()
    
    def _calculate_confidence(self, merchant: str, amount: float, raw_text: str) -> float:
        """Calculate confidence score for parsed item
        
        Args:
            merchant: Merchant name
            amount: Amount in dollars
            raw_text: Original line text
            
        Returns:
            Confidence score 0.0-1.0
        """
        confidence = 0.5  # Base confidence
        
        # Merchant name quality
        if len(merchant) > 2:
            confidence += 0.15
        if len(merchant) > 5:
            confidence += 0.1
        if re.search(self.merchant_indicator_regex, merchant):
            confidence += 0.15
        
        # Amount quality
        if 0.01 <= amount <= 10000:  # Reasonable amount range
            confidence += 0.2
        else:
            confidence -= 0.2
        
        # Text quality
        if len(raw_text) > 5:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def parse_with_items(self, text: str) -> List[Dict]:
        """Parse receipt with item-level details
        
        Args:
            text: Receipt OCR text
            
        Returns:
            List of dictionaries with item details
        """
        expenses = self.parse_receipt_text(text)
        return [item.to_dict() for item in expenses]
    
    def parse_simple(self, text: str) -> List[Dict]:
        """Simple parsing returning just merchant and amount
        
        Args:
            text: Receipt OCR text
            
        Returns:
            List of {merchant, amount} dictionaries
        """
        expenses = self.parse_receipt_text(text)
        return [
            {
                'merchant': item.merchant,
                'amount': item.amount
            }
            for item in expenses
        ]


# Convenience function
def parse_receipt(text: str, simple: bool = False) -> List[Dict]:
    """Parse receipt text into expense data
    
    Args:
        text: Receipt OCR text
        simple: If True, return only merchant and amount
        
    Returns:
        List of parsed expense items
        
    Example:
        >>> text = '''Starbucks $8.20
        ... Uber $18
        ... Amazon $42'''
        >>> items = parse_receipt(text, simple=True)
        >>> items[0]
        {'merchant': 'Starbucks', 'amount': 8.2}
    """
    parser = ReceiptParser()
    if simple:
        return parser.parse_simple(text)
    else:
        return parser.parse_with_items(text)
