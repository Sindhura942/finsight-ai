"""
Financial Analysis AI Module - Usage Examples

Demonstrates various ways to use the financial analyzer for expense analysis
and cost-saving recommendations.
"""

from src.agents.financial_analyzer import (
    FinancialAnalyzer,
    analyze_expenses
)


def example_1_simple_analysis():
    """
    Example 1: Simple Financial Analysis
    
    Analyze a small set of expenses and generate recommendations.
    """
    print("=" * 60)
    print("Example 1: Simple Financial Analysis")
    print("=" * 60)
    
    # Sample expenses
    expenses = [
        {"merchant": "Starbucks", "amount": 8.20, "category": "food"},
        {"merchant": "Uber", "amount": 18.00, "category": "transport"},
        {"merchant": "Amazon", "amount": 42.00, "category": "shopping"}
    ]
    
    # Analyze without LLM
    result = analyze_expenses(expenses, use_llm=False)
    
    # Display results
    print(f"\nTotal Spending: ${result['total_spending']:.2f}")
    print(f"Number of Expenses: {result['expense_count']}")
    print(f"\nCategory Breakdown:")
    for cat in result['category_breakdown']:
        print(f"  {cat['category'].title()}: ${cat['amount']:.2f} ({cat['count']} items, avg ${cat['average']:.2f})")
    
    print(f"\nHighest Spending Category: {result['highest_spending_category'].title()}")
    print(f"Amount: ${result['highest_spending_amount']:.2f}")
    
    if result['recommendations']:
        print("\nRecommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"\n  {i}. {rec['title']}")
            print(f"     Description: {rec['description']}")
            print(f"     Priority: {rec['priority'].upper()}")
            print(f"     Potential Savings: ${rec['potential_savings']:.2f}/month")
            if rec['actionable_steps']:
                print(f"     Action Steps:")
                for step in rec['actionable_steps']:
                    print(f"       - {step}")
    
    print("\n")


def example_2_detailed_analysis_with_breakdown():
    """
    Example 2: Detailed Analysis with Complete Breakdown
    
    Analyze a week of expenses with detailed category breakdown.
    """
    print("=" * 60)
    print("Example 2: Detailed Weekly Expense Analysis")
    print("=" * 60)
    
    # A week of realistic expenses
    expenses = [
        # Food/Dining
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Subway", "amount": 12.00, "category": "food"},
        {"merchant": "Pizza Palace", "amount": 25.00, "category": "food"},
        
        # Transport
        {"merchant": "Uber", "amount": 22.50, "category": "transport"},
        {"merchant": "Lyft", "amount": 18.00, "category": "transport"},
        {"merchant": "Shell Gas", "amount": 45.00, "category": "transport"},
        
        # Groceries
        {"merchant": "Whole Foods", "amount": 75.00, "category": "groceries"},
        
        # Shopping
        {"merchant": "Amazon", "amount": 120.00, "category": "shopping"},
        {"merchant": "Best Buy", "amount": 49.99, "category": "shopping"},
        
        # Entertainment
        {"merchant": "Netflix", "amount": 15.99, "category": "subscriptions"},
        {"merchant": "Movie Ticket", "amount": 15.00, "category": "entertainment"}
    ]
    
    analyzer = FinancialAnalyzer(use_llm=False)
    analysis = analyzer.analyze(expenses)
    
    # Print summary
    print(f"\n{analysis.summary}")
    
    # Print percentages
    print("\nSpending Distribution:")
    for cat in sorted(analysis.category_breakdown, key=lambda x: x.amount, reverse=True):
        bar_length = int(cat.percentage / 2)
        bar = "█" * bar_length
        print(f"  {cat.category.title():15} {bar} {cat.percentage:5.1f}%")
    
    print("\n")


def example_3_identify_spending_patterns():
    """
    Example 3: Identify Spending Patterns
    
    Analyze expenses to identify problematic spending patterns.
    """
    print("=" * 60)
    print("Example 3: Identify Spending Patterns")
    print("=" * 60)
    
    # Expenses showing coffee addiction pattern
    expenses = [
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Cafe Nero", "amount": 6.00, "category": "food"},
        {"merchant": "Local Cafe", "amount": 4.50, "category": "food"},
        {"merchant": "Restaurant", "amount": 50.00, "category": "food"}
    ]
    
    analyzer = FinancialAnalyzer(use_llm=False)
    analysis = analyzer.analyze(expenses)
    
    print(f"\nTotal Food Spending: ${analysis.total_spending:.2f}")
    print(f"Average per Transaction: ${analysis.total_spending / len(expenses):.2f}")
    
    # Find food category
    food_cat = next((c for c in analysis.category_breakdown if c.category == "food"), None)
    if food_cat:
        print(f"\nFood Category Analysis:")
        print(f"  Total: ${food_cat.amount:.2f}")
        print(f"  Transactions: {food_cat.count}")
        print(f"  Average per transaction: ${food_cat.average:.2f}")
        print(f"  Estimated monthly: ${food_cat.amount * 4:.2f}")
    
    # Show recommendations
    if analysis.recommendations:
        print(f"\nRecommendations:")
        for rec in analysis.recommendations:
            if rec.category == "food":
                print(f"  • {rec.title}")
                print(f"    {rec.description}")
                print(f"    Potential monthly savings: ${rec.potential_savings:.2f}")
                for step in rec.actionable_steps:
                    print(f"    → {step}")
    
    print("\n")


def example_4_compare_spending_periods():
    """
    Example 4: Compare Spending Across Periods
    
    Compare spending patterns across different time periods.
    """
    print("=" * 60)
    print("Example 4: Compare Spending Periods")
    print("=" * 60)
    
    # Week 1 expenses
    week1_expenses = [
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Restaurant", "amount": 45.00, "category": "food"},
        {"merchant": "Uber", "amount": 40.00, "category": "transport"},
        {"merchant": "Amazon", "amount": 60.00, "category": "shopping"}
    ]
    
    # Week 2 expenses (more spending)
    week2_expenses = [
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Restaurant", "amount": 65.00, "category": "food"},
        {"merchant": "Uber", "amount": 65.00, "category": "transport"},
        {"merchant": "Amazon", "amount": 120.00, "category": "shopping"}
    ]
    
    analyzer = FinancialAnalyzer(use_llm=False)
    
    print("\nWeek 1 Analysis:")
    analysis1 = analyzer.analyze(week1_expenses)
    print(f"Total Spending: ${analysis1.total_spending:.2f}")
    for cat in sorted(analysis1.category_breakdown, key=lambda x: x.amount, reverse=True):
        print(f"  {cat.category.title()}: ${cat.amount:.2f}")
    
    print("\nWeek 2 Analysis:")
    analysis2 = analyzer.analyze(week2_expenses)
    print(f"Total Spending: ${analysis2.total_spending:.2f}")
    for cat in sorted(analysis2.category_breakdown, key=lambda x: x.amount, reverse=True):
        print(f"  {cat.category.title()}: ${cat.amount:.2f}")
    
    # Calculate difference
    difference = analysis2.total_spending - analysis1.total_spending
    percentage_change = (difference / analysis1.total_spending) * 100
    print(f"\nDifference: ${difference:.2f} ({percentage_change:+.1f}%)")
    
    print("\n")


def example_5_category_focused_analysis():
    """
    Example 5: Focus on Specific Category
    
    Deep dive analysis of a single spending category.
    """
    print("=" * 60)
    print("Example 5: Shopping Category Deep Dive")
    print("=" * 60)
    
    # Shopping category expenses
    expenses = [
        {"merchant": "Amazon", "amount": 50.00, "category": "shopping"},
        {"merchant": "Amazon", "amount": 75.00, "category": "shopping"},
        {"merchant": "Amazon", "amount": 45.00, "category": "shopping"},
        {"merchant": "Best Buy", "amount": 120.00, "category": "shopping"},
        {"merchant": "Target", "amount": 85.00, "category": "shopping"},
        # Also add other categories for context
        {"merchant": "Whole Foods", "amount": 60.00, "category": "groceries"}
    ]
    
    analyzer = FinancialAnalyzer(use_llm=False)
    analysis = analyzer.analyze(expenses)
    
    # Focus on shopping
    shopping = next((c for c in analysis.category_breakdown if c.category == "shopping"), None)
    if shopping:
        print(f"\nShopping Analysis:")
        print(f"  Total Spent: ${shopping.amount:.2f}")
        print(f"  Number of Purchases: {shopping.count}")
        print(f"  Average per Purchase: ${shopping.average:.2f}")
        print(f"  Percentage of Total: {(shopping.amount/analysis.total_spending)*100:.1f}%")
        
        # Monthly projection
        monthly = shopping.amount * 4  # Assuming this is weekly data
        print(f"  Projected Monthly: ${monthly:.2f}")
        print(f"  Projected Yearly: ${monthly * 12:.2f}")
    
    # Show shopping recommendations
    if analysis.recommendations:
        shopping_recs = [r for r in analysis.recommendations if r.category == "shopping"]
        if shopping_recs:
            print(f"\nRecommendations for Shopping:")
            for rec in shopping_recs:
                print(f"  • {rec.title}")
                print(f"    Priority: {rec.priority.upper()}")
                print(f"    Savings Potential: ${rec.potential_savings:.2f}/month")
    
    print("\n")


def example_6_budget_compliance_check():
    """
    Example 6: Check Budget Compliance
    
    Analyze expenses against budget limits.
    """
    print("=" * 60)
    print("Example 6: Budget Compliance Analysis")
    print("=" * 60)
    
    # Set budget limits
    budget_limits = {
        "food": 300.0,
        "transport": 200.0,
        "shopping": 200.0,
        "groceries": 200.0,
        "entertainment": 100.0
    }
    
    # Realistic expenses
    expenses = [
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Lunch", "amount": 15.00, "category": "food"},
        {"merchant": "Dinner", "amount": 40.00, "category": "food"},
        {"merchant": "Grocery Store", "amount": 120.00, "category": "groceries"},
        {"merchant": "Uber", "amount": 25.00, "category": "transport"},
        {"merchant": "Gas", "amount": 50.00, "category": "transport"},
        {"merchant": "Amazon", "amount": 150.00, "category": "shopping"},
        {"merchant": "Netflix", "amount": 15.99, "category": "subscriptions"}
    ]
    
    analyzer = FinancialAnalyzer(use_llm=False)
    analysis = analyzer.analyze(expenses, budget_limits=budget_limits)
    
    print("\nBudget Compliance Report:\n")
    for cat in analysis.category_breakdown:
        budget = budget_limits.get(cat.category, float('inf'))
        spent = cat.amount
        remaining = budget - spent
        percentage = (spent / budget) * 100 if budget != float('inf') else 0
        
        status = "✓ OK" if remaining > 0 else "✗ OVER"
        
        print(f"{cat.category.title()}")
        print(f"  Budget: ${budget:.2f}")
        print(f"  Spent: ${spent:.2f}")
        print(f"  Remaining: ${remaining:.2f} ({status})")
        print(f"  Usage: {percentage:.0f}%")
        print()
    
    print("\n")


def example_7_json_output():
    """
    Example 7: JSON Output for Integration
    
    Get analysis results as JSON for API/database integration.
    """
    print("=" * 60)
    print("Example 7: JSON Output for Integration")
    print("=" * 60)
    
    import json
    
    expenses = [
        {"merchant": "Starbucks", "amount": 8.20, "category": "food"},
        {"merchant": "Uber", "amount": 18.00, "category": "transport"},
        {"merchant": "Amazon", "amount": 42.00, "category": "shopping"}
    ]
    
    analyzer = FinancialAnalyzer(use_llm=False)
    analysis = analyzer.analyze(expenses)
    
    # Convert to JSON
    json_output = json.dumps(analysis.to_dict(), indent=2)
    
    print("\nJSON Output:")
    print(json_output)
    
    print("\n")


def example_8_high_frequency_spending():
    """
    Example 8: Identify High-Frequency Spending
    
    Find frequently repeated small expenses that add up.
    """
    print("=" * 60)
    print("Example 8: High-Frequency Spending Analysis")
    print("=" * 60)
    
    # High-frequency coffee purchases
    expenses = [
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 6.00, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Cafe", "amount": 4.50, "category": "food"}
    ]
    
    analyzer = FinancialAnalyzer(use_llm=False)
    analysis = analyzer.analyze(expenses)
    
    food = next((c for c in analysis.category_breakdown if c.category == "food"), None)
    if food:
        print(f"\nHigh-Frequency Spending Analysis:")
        print(f"  Category: {food.category}")
        print(f"  Total Spent: ${food.amount:.2f}")
        print(f"  Transaction Count: {food.count}")
        print(f"  Average per Transaction: ${food.average:.2f}")
        print(f"  Frequency: {food.count} times")
        
        # Calculate daily/weekly/monthly
        daily_avg = food.amount / 7  # Assuming 7-day period
        weekly_avg = daily_avg * 7
        monthly_projection = daily_avg * 30
        
        print(f"\n  Projected Spending (assuming daily pattern):")
        print(f"    Daily: ${daily_avg:.2f}")
        print(f"    Weekly: ${weekly_avg:.2f}")
        print(f"    Monthly: ${monthly_projection:.2f}")
        print(f"    Yearly: ${monthly_projection * 12:.2f}")
        
        print(f"\n  If reduced to 2x per week:")
        reduced = (2 * 5.50) * 4.33 * 12
        saved = (monthly_projection * 12) - reduced
        print(f"    Yearly Cost: ${reduced:.2f}")
        print(f"    Potential Savings: ${saved:.2f}/year")
    
    print("\n")


def example_9_compare_merchants():
    """
    Example 9: Compare Spending Across Merchants
    
    Analyze which merchants get the most spending.
    """
    print("=" * 60)
    print("Example 9: Merchant Spending Analysis")
    print("=" * 60)
    
    # Expenses from various merchants
    expenses = [
        {"merchant": "Amazon", "amount": 50.00, "category": "shopping"},
        {"merchant": "Amazon", "amount": 75.00, "category": "shopping"},
        {"merchant": "Amazon", "amount": 45.00, "category": "shopping"},
        {"merchant": "Best Buy", "amount": 120.00, "category": "shopping"},
        {"merchant": "Target", "amount": 85.00, "category": "shopping"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Starbucks", "amount": 5.50, "category": "food"},
        {"merchant": "Restaurant", "amount": 40.00, "category": "food"}
    ]
    
    # Group by merchant
    merchant_totals = {}
    for expense in expenses:
        merchant = expense['merchant']
        amount = expense['amount']
        if merchant not in merchant_totals:
            merchant_totals[merchant] = 0
        merchant_totals[merchant] += amount
    
    # Sort by spending
    sorted_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)
    
    print("\nTop Merchants by Spending:\n")
    for i, (merchant, total) in enumerate(sorted_merchants[:5], 1):
        percentage = (total / sum(merchant_totals.values())) * 100
        print(f"  {i}. {merchant:20} ${total:7.2f} ({percentage:5.1f}%)")
    
    print("\n")


def example_10_category_comparison():
    """
    Example 10: Compare All Categories
    
    Show side-by-side comparison of spending by category.
    """
    print("=" * 60)
    print("Example 10: Category Comparison")
    print("=" * 60)
    
    expenses = [
        {"merchant": "Starbucks", "amount": 40.00, "category": "food"},
        {"merchant": "Whole Foods", "amount": 120.00, "category": "groceries"},
        {"merchant": "Uber", "amount": 80.00, "category": "transport"},
        {"merchant": "Amazon", "amount": 150.00, "category": "shopping"},
        {"merchant": "Netflix", "amount": 15.99, "category": "subscriptions"},
        {"merchant": "Electric Bill", "amount": 85.00, "category": "utilities"}
    ]
    
    analyzer = FinancialAnalyzer(use_llm=False)
    analysis = analyzer.analyze(expenses)
    
    print(f"\nTotal Budget: ${analysis.total_spending:.2f}\n")
    
    # Sort by amount
    sorted_cats = sorted(analysis.category_breakdown, key=lambda x: x.amount, reverse=True)
    
    # Print comparison
    print(f"{'Category':<20} {'Amount':>10} {'Count':>6} {'Avg':>10} {'Percentage':>12}")
    print("-" * 60)
    for cat in sorted_cats:
        print(f"{cat.category.title():<20} ${cat.amount:>9.2f} {cat.count:>6} ${cat.average:>9.2f} {cat.percentage:>11.1f}%")
    
    print("\n")


if __name__ == "__main__":
    """Run all examples."""
    
    example_1_simple_analysis()
    example_2_detailed_analysis_with_breakdown()
    example_3_identify_spending_patterns()
    example_4_compare_spending_periods()
    example_5_category_focused_analysis()
    example_6_budget_compliance_check()
    example_7_json_output()
    example_8_high_frequency_spending()
    example_9_compare_merchants()
    example_10_category_comparison()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
