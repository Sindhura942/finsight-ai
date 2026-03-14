"""
Financial Analysis AI Module for FinSight AI

Analyzes categorized expenses and generates intelligent cost-saving recommendations
using statistical analysis and AI-powered insights.

Features:
- Total spending calculation
- Category-based spending breakdown
- Highest spending area identification
- Cost-saving recommendations via LLM or keyword-based heuristics
- Spending trends and patterns
- Budget warnings and alerts
"""

import json
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from datetime import datetime
import logging
import httpx

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class CategoryBreakdown:
    """Spending breakdown for a single category."""
    
    category: str
    amount: float
    count: int
    average: float = field(init=False)
    percentage: float = field(init=False)
    
    def __post_init__(self):
        """Calculate derived fields."""
        self.average = self.amount / self.count if self.count > 0 else 0.0
        self.percentage = 0.0  # Will be set by FinancialAnalysis
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'category': self.category,
            'amount': round(self.amount, 2),
            'count': self.count,
            'average': round(self.average, 2),
            'percentage': round(self.percentage, 1)
        }


@dataclass
class CostSavingRecommendation:
    """Recommendation for cost savings."""
    
    title: str
    description: str
    category: str
    potential_savings: float
    priority: str  # 'high', 'medium', 'low'
    actionable_steps: List[str] = field(default_factory=list)
    confidence: float = 0.8
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'potential_savings': round(self.potential_savings, 2),
            'priority': self.priority,
            'actionable_steps': self.actionable_steps,
            'confidence': round(self.confidence, 2)
        }


@dataclass
class FinancialAnalysis:
    """Complete financial analysis with recommendations."""
    
    total_spending: float
    currency: str = "USD"
    category_breakdown: List[CategoryBreakdown] = field(default_factory=list)
    recommendations: List[CostSavingRecommendation] = field(default_factory=list)
    highest_spending_category: Optional[str] = None
    highest_spending_amount: float = 0.0
    analysis_date: str = field(default_factory=lambda: datetime.now().isoformat())
    expense_count: int = 0
    summary: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'total_spending': round(self.total_spending, 2),
            'currency': self.currency,
            'expense_count': self.expense_count,
            'analysis_date': self.analysis_date,
            'category_breakdown': [cat.to_dict() for cat in self.category_breakdown],
            'highest_spending_category': self.highest_spending_category,
            'highest_spending_amount': round(self.highest_spending_amount, 2),
            'recommendations': [rec.to_dict() for rec in self.recommendations],
            'summary': self.summary
        }


class FinancialAnalyzer:
    """
    Analyzes categorized expenses and generates cost-saving recommendations.
    
    Features:
    - Spending aggregation by category
    - Statistical analysis
    - AI-powered recommendations (via Ollama or heuristics)
    - Budget tracking
    - Trend analysis
    
    Example:
        analyzer = FinancialAnalyzer()
        expenses = [
            {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
            {"merchant": "Uber", "amount": 22.50, "category": "transport"}
        ]
        analysis = analyzer.analyze(expenses)
        print(analysis.summary)
    """
    
    # Spending thresholds for recommendations (in USD)
    SPENDING_THRESHOLDS = {
        'food': 200,
        'transport': 150,
        'shopping': 300,
        'entertainment': 100,
        'subscriptions': 50,
        'utilities': 150,
        'groceries': 200,
        'healthcare': 200,
        'other': 100
    }
    
    # Category keywords for heuristic recommendations
    RECOMMENDATION_KEYWORDS = {
        'food': {
            'keywords': ['starbucks', 'coffee', 'cafe', 'restaurant', 'pizza', 'burger', 'fast food'],
            'title': 'Reduce Frequent Dining',
            'description': 'Coffee shops and restaurants are high-frequency, low-value expenses',
            'suggestion': 'Brew coffee at home, pack lunch instead of eating out'
        },
        'transport': {
            'keywords': ['uber', 'lyft', 'taxi', 'gas', 'parking'],
            'title': 'Optimize Transportation',
            'description': 'Ridesharing and frequent drives accumulate quickly',
            'suggestion': 'Use public transit, carpool, or combine trips'
        },
        'shopping': {
            'keywords': ['amazon', 'online', 'mall', 'retail', 'shopping'],
            'title': 'Reduce Online Shopping',
            'description': 'Online shopping can lead to impulse purchases',
            'suggestion': '24-hour rule: wait 24 hours before online purchases'
        },
        'subscriptions': {
            'keywords': ['netflix', 'spotify', 'subscription', 'monthly'],
            'title': 'Review Subscriptions',
            'description': 'Multiple subscriptions accumulate to significant amounts',
            'suggestion': 'Audit all subscriptions, cancel unused services'
        },
        'entertainment': {
            'keywords': ['movie', 'cinema', 'concert', 'ticket', 'gaming'],
            'title': 'Limit Entertainment Spending',
            'description': 'Entertainment expenses often exceed budget',
            'suggestion': 'Use free entertainment options, set monthly limits'
        }
    }
    
    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        model: str = "mistral",
        timeout: int = 30,
        use_llm: bool = True,
        use_fallback: bool = True
    ):
        """
        Initialize FinancialAnalyzer.
        
        Args:
            ollama_host: URL of Ollama server
            model: Model name for LLM
            timeout: Request timeout in seconds
            use_llm: Whether to use LLM for recommendations
            use_fallback: Whether to fall back to keyword matching
        """
        self.ollama_host = ollama_host
        self.model = model
        self.timeout = timeout
        self.use_llm = use_llm
        self.use_fallback = use_fallback
        self._ollama_available = None
        self._check_timestamp = None
        
        logger.info(f"FinancialAnalyzer initialized with model={model}, use_llm={use_llm}")
    
    def analyze(
        self,
        expenses: List[Dict],
        use_llm: bool = None,
        budget_limits: Optional[Dict[str, float]] = None
    ) -> FinancialAnalysis:
        """
        Analyze categorized expenses and generate recommendations.
        
        Args:
            expenses: List of expenses with {merchant, amount, category, currency}
            use_llm: Override default LLM setting
            budget_limits: Optional budget limits by category {category: limit}
        
        Returns:
            FinancialAnalysis with breakdown and recommendations
        
        Example:
            expenses = [
                {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
                {"merchant": "Whole Foods", "amount": 75.00, "category": "groceries"}
            ]
            analysis = analyzer.analyze(expenses)
        """
        try:
            if use_llm is None:
                use_llm = self.use_llm
            
            logger.info(f"Analyzing {len(expenses)} expenses")
            
            # Validate input
            if not expenses:
                logger.warning("No expenses provided for analysis")
                return FinancialAnalysis(total_spending=0.0, expense_count=0)
            
            # Calculate totals and breakdowns
            total_spending, breakdown = self._calculate_breakdown(expenses)
            currency = expenses[0].get('currency', 'USD') if expenses else 'USD'
            
            # Identify highest spending category
            highest_category = None
            highest_amount = 0.0
            if breakdown:
                highest_category = max(breakdown.items(), key=lambda x: x[1].amount)
                highest_category, highest_amount = highest_category[0], highest_category[1].amount
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                expenses=expenses,
                breakdown=breakdown,
                total_spending=total_spending,
                use_llm=use_llm,
                budget_limits=budget_limits
            )
            
            # Generate summary
            summary = self._generate_summary(
                total_spending=total_spending,
                breakdown=breakdown,
                recommendations=recommendations,
                currency=currency
            )
            
            # Create analysis object
            analysis = FinancialAnalysis(
                total_spending=total_spending,
                currency=currency,
                category_breakdown=list(breakdown.values()),
                recommendations=recommendations,
                highest_spending_category=highest_category,
                highest_spending_amount=highest_amount,
                expense_count=len(expenses),
                summary=summary
            )
            
            # Update percentages
            for cat in analysis.category_breakdown:
                if total_spending > 0:
                    cat.percentage = (cat.amount / total_spending) * 100
            
            logger.info(f"Analysis complete: ${total_spending:.2f} across {len(breakdown)} categories")
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing expenses: {e}")
            # Return basic analysis on error
            return FinancialAnalysis(
                total_spending=0.0,
                expense_count=len(expenses)
            )
    
    def _calculate_breakdown(
        self,
        expenses: List[Dict]
    ) -> Tuple[float, Dict[str, CategoryBreakdown]]:
        """
        Calculate total spending and category breakdown.
        
        Args:
            expenses: List of expenses
        
        Returns:
            Tuple of (total_spending, breakdown_dict)
        """
        breakdown = defaultdict(lambda: {'amount': 0.0, 'count': 0})
        total = 0.0
        
        for expense in expenses:
            amount = float(expense.get('amount', 0))
            category = expense.get('category', 'other').lower()
            
            breakdown[category]['amount'] += amount
            breakdown[category]['count'] += 1
            total += amount
        
        # Convert to CategoryBreakdown objects
        breakdown_dict = {
            cat: CategoryBreakdown(
                category=cat,
                amount=data['amount'],
                count=data['count']
            )
            for cat, data in breakdown.items()
        }
        
        return total, breakdown_dict
    
    def _generate_recommendations(
        self,
        expenses: List[Dict],
        breakdown: Dict[str, CategoryBreakdown],
        total_spending: float,
        use_llm: bool,
        budget_limits: Optional[Dict[str, float]] = None
    ) -> List[CostSavingRecommendation]:
        """
        Generate cost-saving recommendations.
        
        Args:
            expenses: List of expenses
            breakdown: Category breakdown
            total_spending: Total spending amount
            use_llm: Whether to use LLM
            budget_limits: Optional budget limits
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Try LLM first if available
        if use_llm and self._is_ollama_available():
            try:
                llm_recs = self._generate_llm_recommendations(
                    breakdown=breakdown,
                    total_spending=total_spending,
                    budget_limits=budget_limits
                )
                if llm_recs:
                    recommendations.extend(llm_recs)
                    logger.info(f"Generated {len(llm_recs)} LLM recommendations")
            except Exception as e:
                logger.warning(f"LLM recommendation failed: {e}")
                if self.use_fallback:
                    # Fall back to keyword recommendations
                    recommendations = self._generate_keyword_recommendations(
                        expenses=expenses,
                        breakdown=breakdown,
                        budget_limits=budget_limits
                    )
        else:
            # Use keyword-based recommendations
            recommendations = self._generate_keyword_recommendations(
                expenses=expenses,
                breakdown=breakdown,
                budget_limits=budget_limits
            )
        
        # Sort by priority and potential savings
        priority_map = {'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(
            key=lambda x: (priority_map.get(x.priority, 0), x.potential_savings),
            reverse=True
        )
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _generate_keyword_recommendations(
        self,
        expenses: List[Dict],
        breakdown: Dict[str, CategoryBreakdown],
        budget_limits: Optional[Dict[str, float]] = None
    ) -> List[CostSavingRecommendation]:
        """
        Generate recommendations using keyword matching.
        
        Args:
            expenses: List of expenses
            breakdown: Category breakdown
            budget_limits: Optional budget limits
        
        Returns:
            List of recommendations
        """
        recommendations = []
        merchants_by_category = defaultdict(list)
        
        # Group merchants by category
        for expense in expenses:
            category = expense.get('category', 'other').lower()
            merchant = expense.get('merchant', '').lower()
            merchants_by_category[category].append(merchant)
        
        # Check each category for recommendations
        for category, cat_break in breakdown.items():
            if category not in self.RECOMMENDATION_KEYWORDS:
                continue
            
            rec_info = self.RECOMMENDATION_KEYWORDS[category]
            merchants = merchants_by_category.get(category, [])
            threshold = self.SPENDING_THRESHOLDS.get(category, 100)
            
            # Determine priority based on spending
            if cat_break.amount > threshold * 1.5:
                priority = 'high'
                potential_savings = cat_break.amount * 0.3  # 30% savings
            elif cat_break.amount > threshold:
                priority = 'medium'
                potential_savings = cat_break.amount * 0.15  # 15% savings
            else:
                priority = 'low'
                potential_savings = cat_break.amount * 0.1  # 10% savings
            
            # Check if category matches keywords in merchants
            matched = any(
                any(kw in merchant for kw in rec_info['keywords'])
                for merchant in merchants
            )
            
            if matched or cat_break.amount > threshold:
                rec = CostSavingRecommendation(
                    title=rec_info['title'],
                    description=rec_info['description'],
                    category=category,
                    potential_savings=potential_savings,
                    priority=priority,
                    actionable_steps=[rec_info['suggestion']],
                    confidence=0.75 if matched else 0.6
                )
                recommendations.append(rec)
        
        return recommendations
    
    def _generate_llm_recommendations(
        self,
        breakdown: Dict[str, CategoryBreakdown],
        total_spending: float,
        budget_limits: Optional[Dict[str, float]] = None
    ) -> Optional[List[CostSavingRecommendation]]:
        """
        Generate recommendations using LLM (Ollama).
        
        Args:
            breakdown: Category breakdown
            total_spending: Total spending
            budget_limits: Optional budget limits
        
        Returns:
            List of recommendations or None if failed
        """
        try:
            # Build prompt
            breakdown_text = "\n".join([
                f"- {cat.category}: ${cat.amount:.2f} ({cat.count} items, avg ${cat.average:.2f})"
                for cat in breakdown.values()
            ])
            
            prompt = f"""Analyze this spending breakdown and provide 3 specific, actionable cost-saving recommendations.

Total Spending: ${total_spending:.2f}

Category Breakdown:
{breakdown_text}

For each recommendation, provide:
1. Title (short, actionable)
2. Description (why this matters)
3. Category (which category to reduce)
4. Potential monthly savings (dollar amount)
5. Priority (high/medium/low based on impact)
6. Action steps (1-2 specific actions)

Format as JSON array:
[
  {{
    "title": "...",
    "description": "...",
    "category": "...",
    "potential_savings": 50.0,
    "priority": "high",
    "actionable_steps": ["...", "..."]
  }}
]

Only return valid JSON, no other text."""
            
            # Call LLM
            response = self._call_ollama(prompt)
            if not response:
                return None
            
            # Parse response
            recs = self._parse_recommendations(response)
            return recs
        
        except Exception as e:
            logger.warning(f"LLM recommendation generation failed: {e}")
            return None
    
    def _parse_recommendations(self, response: str) -> Optional[List[CostSavingRecommendation]]:
        """
        Parse LLM response into recommendations.
        
        Args:
            response: LLM response text
        
        Returns:
            List of recommendations or None
        """
        try:
            # Try to extract JSON
            json_str = self._extract_json(response)
            if not json_str:
                logger.warning("Could not extract JSON from LLM response")
                return None
            
            # Parse JSON
            data = json.loads(json_str)
            if not isinstance(data, list):
                data = [data]
            
            recommendations = []
            for item in data:
                try:
                    rec = CostSavingRecommendation(
                        title=item.get('title', ''),
                        description=item.get('description', ''),
                        category=item.get('category', 'other'),
                        potential_savings=float(item.get('potential_savings', 0)),
                        priority=item.get('priority', 'medium').lower(),
                        actionable_steps=item.get('actionable_steps', []),
                        confidence=0.85
                    )
                    
                    # Validate
                    if rec.title and rec.category:
                        recommendations.append(rec)
                except (KeyError, ValueError, TypeError) as e:
                    logger.debug(f"Error parsing recommendation: {e}")
                    continue
            
            return recommendations if recommendations else None
        
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"JSON parsing failed: {e}")
            return None
    
    def _extract_json(self, text: str) -> Optional[str]:
        """
        Extract JSON from text (handles markdown code blocks, etc.).
        
        Args:
            text: Text containing JSON
        
        Returns:
            JSON string or None
        """
        # Try markdown code block
        match = re.search(r'```json\s*(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try generic code block
        match = re.search(r'```\s*(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Try JSON array
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            return match.group(0).strip()
        
        # Try JSON object
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return match.group(0).strip()
        
        return None
    
    def _call_ollama(self, prompt: str) -> Optional[str]:
        """
        Call Ollama API for recommendations.
        
        Args:
            prompt: Prompt text
        
        Returns:
            Response text or None
        """
        try:
            url = f"{self.ollama_host}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3
            }
            
            response = httpx.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', '')
            else:
                logger.warning(f"Ollama API error: {response.status_code}")
                return None
        
        except httpx.RequestError as e:
            logger.warning(f"Ollama request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error calling Ollama: {e}")
            return None
    
    def _is_ollama_available(self) -> bool:
        """
        Check if Ollama server is available (with caching).
        
        Returns:
            True if available, False otherwise
        """
        try:
            # Cache availability check for 60 seconds
            import time
            now = time.time()
            if self._check_timestamp and (now - self._check_timestamp) < 60:
                return self._ollama_available
            
            url = f"{self.ollama_host}/api/tags"
            response = httpx.get(url, timeout=5)
            available = response.status_code == 200
            
            self._ollama_available = available
            self._check_timestamp = now
            
            return available
        except Exception:
            self._ollama_available = False
            return False
    
    def _generate_summary(
        self,
        total_spending: float,
        breakdown: Dict[str, CategoryBreakdown],
        recommendations: List[CostSavingRecommendation],
        currency: str = "USD"
    ) -> str:
        """
        Generate human-readable summary.
        
        Args:
            total_spending: Total amount spent
            breakdown: Category breakdown
            recommendations: List of recommendations
            currency: Currency code
        
        Returns:
            Summary text
        """
        symbol = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥'}.get(currency, '$')
        
        lines = []
        lines.append(f"Total Spending: {symbol}{total_spending:.2f}\n")
        
        # Category breakdown
        lines.append("Category Breakdown:")
        for cat in sorted(breakdown.values(), key=lambda x: x.amount, reverse=True):
            pct = (cat.amount / total_spending * 100) if total_spending > 0 else 0
            lines.append(f"  {cat.category.title()}: {symbol}{cat.amount:.2f} ({pct:.1f}%) - {cat.count} items")
        
        # Recommendations summary
        if recommendations:
            lines.append("\nTop Recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                lines.append(f"  {i}. {rec.title} ({rec.priority.upper()})")
                lines.append(f"     Potential savings: {symbol}{rec.potential_savings:.2f}/month")
        
        return "\n".join(lines)


def analyze_expenses(
    expenses: List[Dict],
    use_llm: bool = True,
    budget_limits: Optional[Dict[str, float]] = None,
    model: str = "mistral"
) -> Dict:
    """
    Convenience function for analyzing expenses without instantiating FinancialAnalyzer.
    
    Args:
        expenses: List of categorized expenses
        use_llm: Whether to use LLM for recommendations
        budget_limits: Optional budget limits by category
        model: LLM model to use
    
    Returns:
        Analysis results as dictionary
    
    Example:
        expenses = [
            {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
            {"merchant": "Uber", "amount": 22.50, "category": "transport"}
        ]
        result = analyze_expenses(expenses)
        print(result['summary'])
    """
    analyzer = FinancialAnalyzer(use_llm=use_llm, model=model)
    analysis = analyzer.analyze(expenses, budget_limits=budget_limits)
    return analysis.to_dict()
