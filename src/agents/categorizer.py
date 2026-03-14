"""Categorizer Agent for expense categorization"""

from typing import Optional

from .llm_agent import LLMAgent
from src.prompts import get_prompt, format_prompt
from src.utils import get_logger

logger = get_logger("CategorizerAgent")


class CategorizerAgent(LLMAgent):
    """Agent for categorizing expenses"""

    def __init__(self):
        """Initialize categorizer agent"""
        super().__init__(temperature=0.1)  # Low temperature for consistency

    def categorize(self, merchant_name: str, description: str = "") -> Optional[str]:
        """Categorize an expense
        
        Args:
            merchant_name: Name of merchant
            description: Optional description
            
        Returns:
            Category name
        """
        try:
            prompt_template = get_prompt("categorize")
            if not prompt_template:
                logger.error("Categorize prompt not found")
                return "Other"
            
            prompt = format_prompt(
                prompt_template,
                merchant_name=merchant_name,
                description=description,
            )
            
            response = self.generate(prompt, temperature=0.1).strip()
            
            # Validate response is a known category
            valid_categories = [
                "Food & Dining",
                "Transportation",
                "Shopping",
                "Entertainment",
                "Utilities",
                "Healthcare",
                "Personal Care",
                "Education",
                "Travel",
                "Subscriptions",
                "Other",
            ]
            
            if response in valid_categories:
                logger.info(f"Categorized '{merchant_name}' as '{response}'")
                return response
            
            logger.warning(f"Invalid category returned: {response}")
            return "Other"
        
        except Exception as e:
            logger.error(f"Categorization failed: {str(e)}")
            return "Other"

    def batch_categorize(self, items: list) -> list:
        """Categorize multiple expenses
        
        Args:
            items: List of dicts with merchant_name and optional description
            
        Returns:
            List of categorized items
        """
        results = []
        for item in items:
            category = self.categorize(
                item.get("merchant_name", ""),
                item.get("description", ""),
            )
            results.append({
                **item,
                "category": category,
            })
        return results
