"""Base LLM Agent for communicating with Ollama"""

import json
from typing import Optional, Dict, Any

import requests

from src.config import get_settings
from src.utils import get_logger
from src.prompts import get_prompt, format_prompt

logger = get_logger("LLMAgent")


class LLMAgent:
    """Base agent for LLM operations"""

    def __init__(self, model: str = None, temperature: float = None):
        """Initialize LLM agent
        
        Args:
            model: Model name (uses default if not provided)
            temperature: Temperature for responses
        """
        self.settings = get_settings()
        self.model = model or self.settings.ollama_model
        self.base_url = self.settings.ollama_base_url
        self.temperature = temperature or self.settings.llm_temperature

    def generate(self, prompt: str, temperature: float = None) -> str:
        """Generate response from LLM
        
        Args:
            prompt: Prompt text
            temperature: Optional temperature override
            
        Returns:
            Generated response
        """
        try:
            temp = temperature or self.temperature
            logger.info(f"Generating response with temperature: {temp}")
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temp,
                    "stream": False,
                },
                timeout=30,
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to Ollama at {self.base_url}")
            raise
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            raise

    def generate_json(self, prompt: str, temperature: float = None) -> Dict[str, Any]:
        """Generate JSON response from LLM
        
        Args:
            prompt: Prompt text
            temperature: Optional temperature override
            
        Returns:
            Parsed JSON response
        """
        response = self.generate(prompt, temperature)
        
        try:
            # Find JSON in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            
            # Try as array
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            
            logger.warning("No JSON found in response")
            return {}
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return {}

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
