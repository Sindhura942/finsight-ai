"""LLM Prompt templates for FinSight AI"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PromptTemplate:
    """Base prompt template"""
    name: str
    description: str
    template: str
    temperature: float = 0.3


# ==================== Receipt Processing Prompts ====================

EXTRACT_MERCHANT_PROMPT = PromptTemplate(
    name="extract_merchant",
    description="Extract merchant name from receipt text",
    template="""Extract the merchant/store name from this receipt text.
Return only the merchant name, nothing else.

Receipt text:
{text}

Merchant name:""",
    temperature=0.1,
)


EXTRACT_AMOUNT_PROMPT = PromptTemplate(
    name="extract_amount",
    description="Extract transaction amount from receipt text",
    template="""Extract the total amount/price from this receipt text.
Return only the numeric amount (e.g., 5.50), nothing else.

Receipt text:
{text}

Amount:""",
    temperature=0.1,
)


EXTRACT_RECEIPT_DETAILS_PROMPT = PromptTemplate(
    name="extract_receipt_details",
    description="Extract merchant and amount from receipt",
    template="""Extract merchant name and total amount from this receipt text.
Return JSON with keys 'merchant_name' (string) and 'amount' (float).
If amount is not found, use 0.0.

Receipt text:
{text}

JSON response:""",
    temperature=0.1,
)


# ==================== Categorization Prompts ====================

CATEGORIZE_EXPENSE_PROMPT = PromptTemplate(
    name="categorize_expense",
    description="Categorize an expense",
    template="""Categorize this expense into one of these categories:
Food & Dining
Transportation
Shopping
Entertainment
Utilities
Healthcare
Personal Care
Education
Travel
Subscriptions
Other

Merchant: {merchant_name}
Description: {description}

Return only the category name, nothing else.""",
    temperature=0.1,
)


# ==================== Analysis Prompts ====================

ANALYZE_SPENDING_PROMPT = PromptTemplate(
    name="analyze_spending",
    description="Analyze spending patterns",
    template="""Analyze the following spending data and identify patterns:

{spending_data}

Provide 3-5 key insights about the spending patterns.""",
    temperature=0.7,
)


# ==================== Recommendations Prompts ====================

GENERATE_RECOMMENDATIONS_PROMPT = PromptTemplate(
    name="generate_recommendations",
    description="Generate cost-saving recommendations",
    template="""Based on the following spending data, provide 3-5 specific, actionable cost-saving recommendations.
Format as JSON array with objects containing 'title', 'description', 'potential_savings' (number), and 'priority' (high/medium/low).

Spending Data:
{spending_data}

JSON response:""",
    temperature=0.7,
)


IMPROVE_BUDGET_PROMPT = PromptTemplate(
    name="improve_budget",
    description="Suggest budget improvements",
    template="""Based on these spending patterns, suggest how to improve the budget:

{spending_summary}

Categories with highest spending:
{top_categories}

Provide 5 specific, measurable recommendations.""",
    temperature=0.7,
)


# ==================== Financial Analysis Prompts ====================

DETECT_ANOMALY_PROMPT = PromptTemplate(
    name="detect_anomaly",
    description="Detect unusual spending",
    template="""Analyze these expenses and identify any unusual or anomalous spending:

Average spending per category: {category_averages}
Recent transactions: {recent_transactions}

Flag any transactions that seem unusual compared to history.""",
    temperature=0.3,
)


# Prompt registry
PROMPTS = {
    "extract_merchant": EXTRACT_MERCHANT_PROMPT,
    "extract_amount": EXTRACT_AMOUNT_PROMPT,
    "extract_receipt": EXTRACT_RECEIPT_DETAILS_PROMPT,
    "categorize": CATEGORIZE_EXPENSE_PROMPT,
    "analyze_spending": ANALYZE_SPENDING_PROMPT,
    "recommendations": GENERATE_RECOMMENDATIONS_PROMPT,
    "budget_improvement": IMPROVE_BUDGET_PROMPT,
    "detect_anomaly": DETECT_ANOMALY_PROMPT,
}


def get_prompt(name: str) -> Optional[PromptTemplate]:
    """Get prompt template by name
    
    Args:
        name: Prompt name
        
    Returns:
        Prompt template or None
    """
    return PROMPTS.get(name)


def format_prompt(prompt: PromptTemplate, **kwargs) -> str:
    """Format prompt template with variables
    
    Args:
        prompt: Prompt template
        **kwargs: Variables to format
        
    Returns:
        Formatted prompt string
    """
    return prompt.template.format(**kwargs)


def list_prompts() -> list:
    """List all available prompts
    
    Returns:
        List of prompt names
    """
    return list(PROMPTS.keys())
