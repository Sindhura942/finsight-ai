"""AI agent for expense categorization using Ollama"""

import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field
import httpx

from src.utils import get_logger

logger = get_logger("CategorizerAgent")


@dataclass
class CategorizedExpense:
    """Expense with category assignment"""
    merchant: str
    amount: float
    category: str
    currency: str = "USD"
    confidence: float = 1.0
    reasoning: Optional[str] = None
    raw_response: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


class CategorizerAgent:
    """AI agent for categorizing expenses using Ollama"""
    
    # Available expense categories
    CATEGORIES = {
        "food",
        "groceries",
        "transport",
        "shopping",
        "subscriptions",
        "utilities",
        "entertainment",
        "healthcare",
        "other"
    }
    
    # Category keywords for fallback classification
    CATEGORY_KEYWORDS = {
        "food": [
            "starbucks", "coffee", "cafe", "restaurant", "pizza", "burger",
            "mcdonald", "subway", "diner", "bistro", "bar", "pub", "lunch",
            "dinner", "breakfast", "meal", "food", "eating", "drink"
        ],
        "groceries": [
            "whole foods", "trader joe", "safeway", "kroger", "publix",
            "grocery", "market", "walmart", "target", "costco", "store",
            "supermarket", "shopping"
        ],
        "transport": [
            "uber", "lyft", "taxi", "cab", "bus", "transit", "parking",
            "gas station", "fuel", "shell", "chevron", "aaa", "airline",
            "train", "metro", "car", "vehicle"
        ],
        "shopping": [
            "amazon", "ebay", "mall", "shop", "retail", "store", "outlet",
            "best buy", "home depot", "lowes", "ikea", "clothing",
            "department"
        ],
        "subscriptions": [
            "netflix", "spotify", "hulu", "disney", "subscription",
            "membership", "subscription"
        ],
        "utilities": [
            "electric", "water", "gas", "internet", "phone", "utility",
            "comcast", "verizon", "at&t", "provider", "bill"
        ],
        "entertainment": [
            "movie", "cinema", "theater", "concert", "music", "gaming",
            "game", "entertainment", "event", "ticket", "show"
        ],
        "healthcare": [
            "pharmacy", "doctor", "hospital", "medical", "health",
            "clinic", "dentist", "eye", "care", "wellness"
        ]
    }
    
    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 30,
        use_fallback: bool = True
    ):
        """Initialize categorizer agent
        
        Args:
            ollama_host: URL to Ollama server
            model: Model name (e.g., "mistral", "llama2", "neural-chat")
            timeout: Request timeout in seconds
            use_fallback: Use keyword-based fallback if LLM unavailable
        """
        self.ollama_host = ollama_host
        self.model = model
        self.timeout = timeout
        self.use_fallback = use_fallback
        self._ollama_available = None
        
        logger.info(f"Initializing CategorizerAgent with model: {model}")
    
    def categorize_expenses(
        self,
        expenses: List[Dict],
        use_llm: bool = True
    ) -> List[CategorizedExpense]:
        """Categorize list of expenses
        
        Args:
            expenses: List of {"merchant", "amount", ...} dictionaries
            use_llm: Use LLM for categorization (falls back to keywords if unavailable)
            
        Returns:
            List of CategorizedExpense objects with categories
            
        Example:
            >>> expenses = [
            ...     {"merchant": "Starbucks", "amount": 8},
            ...     {"merchant": "Uber", "amount": 18}
            ... ]
            >>> agent = CategorizerAgent()
            >>> categorized = agent.categorize_expenses(expenses)
            >>> categorized[0].category
            'food'
        """
        if not expenses:
            logger.warning("Empty expenses list provided")
            return []
        
        logger.info(f"Categorizing {len(expenses)} expenses")
        
        categorized = []
        
        # Try batch processing if possible
        if use_llm and self._is_ollama_available():
            try:
                batch_result = self._categorize_batch_llm(expenses)
                if batch_result:
                    return batch_result
            except Exception as e:
                logger.warning(f"Batch LLM categorization failed: {e}")
                if not self.use_fallback:
                    raise
        
        # Fall back to individual categorization
        for expense in expenses:
            try:
                if use_llm and self._is_ollama_available():
                    categorized_item = self._categorize_single_llm(expense)
                else:
                    categorized_item = self._categorize_single_keyword(expense)
                
                if categorized_item:
                    categorized.append(categorized_item)
            except Exception as e:
                logger.error(f"Failed to categorize {expense.get('merchant')}: {e}")
                # Add with fallback category
                if self.use_fallback:
                    fallback = self._categorize_single_keyword(expense)
                    if fallback:
                        categorized.append(fallback)
        
        logger.info(f"Successfully categorized {len(categorized)} expenses")
        return categorized
    
    def _is_ollama_available(self) -> bool:
        """Check if Ollama server is available"""
        if self._ollama_available is not None:
            return self._ollama_available
        
        try:
            response = httpx.get(
                f"{self.ollama_host}/api/tags",
                timeout=self.timeout
            )
            self._ollama_available = response.status_code == 200
            if self._ollama_available:
                logger.info(f"Ollama server available at {self.ollama_host}")
        except Exception as e:
            logger.warning(f"Ollama server not available: {e}")
            self._ollama_available = False
        
        return self._ollama_available
    
    def _categorize_batch_llm(self, expenses: List[Dict]) -> Optional[List[CategorizedExpense]]:
        """Categorize expenses using LLM in batch mode
        
        Args:
            expenses: List of expenses to categorize
            
        Returns:
            List of categorized expenses or None if failed
        """
        prompt = self._build_batch_prompt(expenses)
        
        try:
            response = self._call_ollama(prompt)
            return self._parse_batch_response(response, expenses)
        except Exception as e:
            logger.error(f"Batch LLM categorization failed: {e}")
            return None
    
    def _categorize_single_llm(self, expense: Dict) -> Optional[CategorizedExpense]:
        """Categorize single expense using LLM
        
        Args:
            expense: Single expense to categorize
            
        Returns:
            CategorizedExpense or None if failed
        """
        prompt = self._build_single_prompt(expense)
        
        try:
            response = self._call_ollama(prompt)
            return self._parse_single_response(response, expense)
        except Exception as e:
            logger.error(f"LLM categorization failed for {expense.get('merchant')}: {e}")
            return None
    
    def _categorize_single_keyword(self, expense: Dict) -> Optional[CategorizedExpense]:
        """Fallback: categorize using keyword matching
        
        Args:
            expense: Single expense to categorize
            
        Returns:
            CategorizedExpense
        """
        merchant = expense.get("merchant", "").lower()
        amount = expense.get("amount", 0)
        
        # Try to find matching category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in merchant:
                    confidence = 0.7  # Lower confidence for keyword-based
                    return CategorizedExpense(
                        merchant=expense.get("merchant", "Unknown"),
                        amount=amount,
                        category=category,
                        currency=expense.get("currency", "USD"),
                        confidence=confidence,
                        reasoning=f"Keyword matched: {keyword}"
                    )
        
        # Default to "other"
        logger.warning(f"No category match found for {merchant}, defaulting to 'other'")
        return CategorizedExpense(
            merchant=expense.get("merchant", "Unknown"),
            amount=amount,
            category="other",
            currency=expense.get("currency", "USD"),
            confidence=0.5,
            reasoning="No keyword match found"
        )
    
    def _build_single_prompt(self, expense: Dict) -> str:
        """Build prompt for single expense categorization
        
        Args:
            expense: Single expense
            
        Returns:
            Prompt string
        """
        merchant = expense.get("merchant", "Unknown")
        amount = expense.get("amount", 0)
        
        categories = ", ".join(sorted(self.CATEGORIES))
        
        prompt = f"""Categorize this expense into one of these categories: {categories}

Expense:
Merchant: {merchant}
Amount: ${amount}

Respond with ONLY valid JSON (no markdown, no extra text):
{{
  "category": "<one of the categories above>",
  "confidence": <0.0 to 1.0>,
  "reasoning": "<brief explanation>"
}}"""
        
        return prompt
    
    def _build_batch_prompt(self, expenses: List[Dict]) -> str:
        """Build prompt for batch expense categorization
        
        Args:
            expenses: List of expenses
            
        Returns:
            Prompt string
        """
        categories = ", ".join(sorted(self.CATEGORIES))
        
        expenses_json = json.dumps(expenses, indent=2)
        
        prompt = f"""Categorize these expenses into one of these categories: {categories}

Expenses:
{expenses_json}

Respond with ONLY valid JSON array (no markdown, no extra text):
[
  {{
    "merchant": "<merchant name>",
    "category": "<one of the categories above>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<brief explanation>"
  }},
  ...
]"""
        
        return prompt
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to get categorization
        
        Args:
            prompt: Prompt for the model
            
        Returns:
            Model response text
            
        Raises:
            Exception: If API call fails
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "temperature": 0.3,  # Low temperature for consistent categorization
            "top_p": 0.9
        }
        
        logger.debug(f"Calling Ollama with model: {self.model}")
        
        response = httpx.post(
            f"{self.ollama_host}/api/generate",
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        result = response.json()
        
        return result.get("response", "")
    
    def _parse_single_response(
        self,
        response: str,
        expense: Dict
    ) -> Optional[CategorizedExpense]:
        """Parse LLM response for single expense
        
        Args:
            response: LLM response text
            expense: Original expense
            
        Returns:
            CategorizedExpense or None if parsing failed
        """
        try:
            # Try to extract JSON from response
            json_str = self._extract_json(response)
            if not json_str:
                logger.warning(f"No JSON found in response: {response[:100]}")
                return None
            
            data = json.loads(json_str)
            
            category = data.get("category", "").lower().strip()
            if category not in self.CATEGORIES:
                logger.warning(f"Invalid category from LLM: {category}")
                category = "other"
            
            confidence = float(data.get("confidence", 0.8))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to 0-1
            
            reasoning = data.get("reasoning", "LLM categorization")
            
            return CategorizedExpense(
                merchant=expense.get("merchant", "Unknown"),
                amount=expense.get("amount", 0),
                category=category,
                currency=expense.get("currency", "USD"),
                confidence=confidence,
                reasoning=reasoning,
                raw_response=response
            )
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.debug(f"Response: {response}")
            return None
    
    def _parse_batch_response(
        self,
        response: str,
        expenses: List[Dict]
    ) -> Optional[List[CategorizedExpense]]:
        """Parse LLM response for batch categorization
        
        Args:
            response: LLM response text
            expenses: Original expenses list
            
        Returns:
            List of CategorizedExpense or None if parsing failed
        """
        try:
            # Try to extract JSON array from response
            json_str = self._extract_json(response)
            if not json_str:
                logger.warning(f"No JSON found in batch response: {response[:100]}")
                return None
            
            data = json.loads(json_str)
            if not isinstance(data, list):
                logger.warning("LLM response is not a JSON array")
                return None
            
            categorized = []
            for i, item in enumerate(data):
                if i >= len(expenses):
                    break
                
                expense = expenses[i]
                category = item.get("category", "").lower().strip()
                
                if category not in self.CATEGORIES:
                    logger.warning(f"Invalid category in batch: {category}")
                    category = "other"
                
                confidence = float(item.get("confidence", 0.8))
                confidence = max(0.0, min(1.0, confidence))
                
                reasoning = item.get("reasoning", "LLM categorization")
                
                categorized.append(CategorizedExpense(
                    merchant=expense.get("merchant", "Unknown"),
                    amount=expense.get("amount", 0),
                    category=category,
                    currency=expense.get("currency", "USD"),
                    confidence=confidence,
                    reasoning=reasoning,
                    raw_response=response
                ))
            
            return categorized if categorized else None
        
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            logger.error(f"Failed to parse batch response: {e}")
            logger.debug(f"Response: {response}")
            return None
    
    @staticmethod
    def _extract_json(text: str) -> Optional[str]:
        """Extract JSON from text that may contain markdown or other content
        
        Args:
            text: Text potentially containing JSON
            
        Returns:
            JSON string or None
        """
        # Try to find JSON in markdown code blocks
        markdown_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if markdown_match:
            return markdown_match.group(1).strip()
        
        # Try to find JSON array
        array_match = re.search(r'\[[\s\S]*\]', text)
        if array_match:
            try:
                json.loads(array_match.group(0))
                return array_match.group(0)
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object
        object_match = re.search(r'\{[\s\S]*\}', text)
        if object_match:
            try:
                json.loads(object_match.group(0))
                return object_match.group(0)
            except json.JSONDecodeError:
                pass
        
        # Return original if it's valid JSON
        try:
            json.loads(text)
            return text
        except json.JSONDecodeError:
            return None
    
    def get_categories(self) -> List[str]:
        """Get list of available categories
        
        Returns:
            Sorted list of category names
        """
        return sorted(self.CATEGORIES)
    
    def add_category(self, category: str, keywords: List[str]):
        """Add new category with keywords
        
        Args:
            category: Category name
            keywords: List of keywords for this category
        """
        if category in self.CATEGORIES:
            logger.warning(f"Category {category} already exists")
            return
        
        self.CATEGORIES.add(category)
        self.CATEGORY_KEYWORDS[category] = [k.lower() for k in keywords]
        logger.info(f"Added category: {category}")


def categorize_expenses(
    expenses: List[Dict],
    model: str = "mistral",
    use_llm: bool = True
) -> List[Dict]:
    """Convenience function to categorize expenses
    
    Args:
        expenses: List of expense dictionaries
        model: Ollama model to use
        use_llm: Use LLM for categorization
        
    Returns:
        List of categorized expense dictionaries
        
    Example:
        >>> expenses = [
        ...     {"merchant": "Starbucks", "amount": 8},
        ...     {"merchant": "Uber", "amount": 18}
        ... ]
        >>> categorized = categorize_expenses(expenses)
        >>> categorized[0]
        {'merchant': 'Starbucks', 'amount': 8, 'category': 'food', ...}
    """
    agent = CategorizerAgent(model=model)
    result = agent.categorize_expenses(expenses, use_llm=use_llm)
    return [item.to_dict() for item in result]
