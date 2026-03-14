"""LLM service for interacting with Ollama/Llama3"""

import json
from typing import Optional

import requests

from app.core.config import settings
from app.core.logger import app_logger


class LLMService:
    """Service for LLM operations using Ollama"""

    def __init__(self, base_url: str = None, model: str = None):
        """Initialize LLM service
        
        Args:
            base_url: Ollama API base URL
            model: Model name to use
        """
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.logger = app_logger

    def extract_expense_details(self, text: str) -> dict:
        """Extract merchant name and amount from receipt text
        
        Args:
            text: Receipt text from OCR
            
        Returns:
            Dictionary with extracted merchant_name and amount
        """
        prompt = f"""Extract merchant name and amount from this receipt text.
Return JSON with keys 'merchant_name' (string) and 'amount' (float).
If amount is not found, use 0.0.

Receipt text:
{text}

JSON response:"""

        try:
            response = self._call_llm(prompt, temperature=0.1)
            
            # Parse JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                self.logger.info(f"Extracted expense: {result}")
                return result
            
            return {"merchant_name": "Unknown", "amount": 0.0}
        
        except Exception as e:
            self.logger.error(f"Failed to extract expense details: {str(e)}")
            return {"merchant_name": "Unknown", "amount": 0.0}

    def categorize_expense(self, merchant_name: str, description: str = "") -> str:
        """Categorize expense using LLM
        
        Args:
            merchant_name: Name of the merchant
            description: Additional description
            
        Returns:
            Category string
        """
        from app.core.constants import EXPENSE_CATEGORIES

        categories_str = ", ".join(EXPENSE_CATEGORIES)
        
        prompt = f"""Categorize this expense into one of these categories:
{categories_str}

Merchant: {merchant_name}
Description: {description}

Return only the category name, nothing else."""

        try:
            response = self._call_llm(prompt, temperature=0.1).strip()
            
            # Ensure response is in valid categories
            if response in EXPENSE_CATEGORIES:
                self.logger.info(f"Categorized {merchant_name} as {response}")
                return response
            
            return "Other"
        
        except Exception as e:
            self.logger.error(f"Failed to categorize expense: {str(e)}")
            return "Other"

    def generate_recommendations(self, spending_data: str) -> list:
        """Generate cost-saving recommendations based on spending
        
        Args:
            spending_data: Summary of spending patterns
            
        Returns:
            List of recommendations
        """
        prompt = f"""Based on the following spending data, provide 3-5 specific, actionable cost-saving recommendations.
Format as JSON array with objects containing 'title', 'description', 'potential_savings' (number), and 'priority' (high/medium/low).

Spending Data:
{spending_data}

JSON response:"""

        try:
            response = self._call_llm(prompt, temperature=0.7)
            
            # Parse JSON array
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                recommendations = json.loads(json_str)
                self.logger.info(f"Generated {len(recommendations)} recommendations")
                return recommendations
            
            return []
        
        except Exception as e:
            self.logger.error(f"Failed to generate recommendations: {str(e)}")
            return []

    def _call_llm(self, prompt: str, temperature: float = 0.5) -> str:
        """Call Ollama LLM API
        
        Args:
            prompt: Prompt to send to LLM
            temperature: Temperature parameter for response generation
            
        Returns:
            LLM response text
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except requests.exceptions.ConnectionError:
            self.logger.error(f"Failed to connect to Ollama at {self.base_url}")
            raise
        except Exception as e:
            self.logger.error(f"LLM call failed: {str(e)}")
            raise

    def health_check(self) -> bool:
        """Check if Ollama service is running
        
        Returns:
            True if service is accessible
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
