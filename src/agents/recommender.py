"""Recommender Agent for cost-saving suggestions"""

import json
from typing import List, Optional, Dict

from .llm_agent import LLMAgent
from src.prompts import get_prompt, format_prompt
from src.utils import get_logger

logger = get_logger("RecommenderAgent")


class RecommenderAgent(LLMAgent):
    """Agent for generating cost-saving recommendations"""

    def __init__(self):
        """Initialize recommender agent"""
        super().__init__(temperature=0.7)

    def generate_recommendations(self, spending_data: str) -> Optional[List[Dict]]:
        """Generate cost-saving recommendations
        
        Args:
            spending_data: Formatted spending summary
            
        Returns:
            List of recommendations
        """
        try:
            prompt_template = get_prompt("recommendations")
            if not prompt_template:
                logger.error("Recommendations prompt not found")
                return []
            
            prompt = format_prompt(prompt_template, spending_data=spending_data)
            response = self.generate(prompt)
            
            # Parse JSON response
            recommendations = self.generate_json(prompt)
            
            if isinstance(recommendations, list):
                logger.info(f"Generated {len(recommendations)} recommendations")
                return recommendations
            
            logger.warning("Invalid recommendations format")
            return []
        
        except Exception as e:
            logger.error(f"Recommendation generation failed: {str(e)}")
            return []

    def suggest_budget_improvements(
        self,
        spending_summary: str,
        top_categories: List[Dict],
    ) -> Optional[str]:
        """Suggest budget improvements
        
        Args:
            spending_summary: Spending summary text
            top_categories: Top spending categories
            
        Returns:
            Budget improvement suggestions
        """
        try:
            # Format top categories
            top_cats_str = "\n".join([
                f"{c.get('category', 'Unknown')}: ${c.get('total_amount', 0):.2f}"
                for c in top_categories[:5]
            ])
            
            prompt_template = get_prompt("budget_improvement")
            if not prompt_template:
                logger.error("Budget improvement prompt not found")
                return None
            
            prompt = format_prompt(
                prompt_template,
                spending_summary=spending_summary,
                top_categories=top_cats_str,
            )
            
            response = self.generate(prompt)
            logger.info("Budget improvements suggested")
            
            return response
        
        except Exception as e:
            logger.error(f"Budget improvement suggestion failed: {str(e)}")
            return None

    def prioritize_recommendations(self, recommendations: List[Dict]) -> List[Dict]:
        """Prioritize recommendations by impact
        
        Args:
            recommendations: List of recommendations
            
        Returns:
            Sorted recommendations
        """
        # Sort by potential savings (descending)
        return sorted(
            recommendations,
            key=lambda x: x.get("potential_savings", 0),
            reverse=True,
        )
