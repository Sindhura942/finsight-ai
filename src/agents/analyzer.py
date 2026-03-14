"""Analyzer Agent for spending analysis"""

from typing import Dict, List, Optional

from .llm_agent import LLMAgent
from src.prompts import get_prompt, format_prompt
from src.utils import get_logger

logger = get_logger("AnalyzerAgent")


class AnalyzerAgent(LLMAgent):
    """Agent for analyzing spending patterns"""

    def __init__(self):
        """Initialize analyzer agent"""
        super().__init__(temperature=0.7)

    def analyze_spending(self, spending_data: str) -> Optional[str]:
        """Analyze spending patterns
        
        Args:
            spending_data: Formatted spending information
            
        Returns:
            Analysis insights
        """
        try:
            prompt_template = get_prompt("analyze_spending")
            if not prompt_template:
                logger.error("Analyze prompt not found")
                return None
            
            prompt = format_prompt(prompt_template, spending_data=spending_data)
            response = self.generate(prompt)
            
            logger.info("Spending analysis complete")
            return response
        
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return None

    def detect_anomalies(
        self,
        category_averages: Dict[str, float],
        recent_transactions: List[Dict],
    ) -> Optional[List[Dict]]:
        """Detect unusual spending patterns
        
        Args:
            category_averages: Average spending by category
            recent_transactions: Recent transactions to analyze
            
        Returns:
            List of anomalies detected
        """
        try:
            # Format data for prompt
            avg_str = "\n".join([f"{k}: ${v:.2f}" for k, v in category_averages.items()])
            trans_str = "\n".join([
                f"{t.get('merchant')}: ${t.get('amount', 0):.2f} ({t.get('category')})"
                for t in recent_transactions[:10]
            ])
            
            prompt_template = get_prompt("detect_anomaly")
            if not prompt_template:
                logger.error("Anomaly detection prompt not found")
                return None
            
            prompt = format_prompt(
                prompt_template,
                category_averages=avg_str,
                recent_transactions=trans_str,
            )
            
            response = self.generate(prompt)
            logger.info("Anomaly detection complete")
            
            return response
        
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return None
