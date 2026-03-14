"""Examples for categorizer agent"""

from src.agents import CategorizerAgent, categorize_expenses


def example_simple_categorization():
    """Example: Simple categorization without LLM"""
    print("=" * 70)
    print("Example 1: Simple Categorization (Keyword-Based)")
    print("=" * 70)
    
    expenses = [
        {"merchant": "Starbucks", "amount": 8},
        {"merchant": "Uber", "amount": 18},
        {"merchant": "Amazon", "amount": 42}
    ]
    
    # Use convenience function
    categorized = categorize_expenses(expenses, use_llm=False)
    
    print("\nInput:")
    for exp in expenses:
        print(f"  {exp['merchant']}: ${exp['amount']}")
    
    print("\nCategorized Output:")
    for item in categorized:
        print(f"  {item['merchant']:20} ${item['amount']:6.2f}  →  {item['category']:15} (confidence: {item['confidence']:.0%})")


def example_detailed_categorization():
    """Example: Detailed categorization with reasoning"""
    print("\n" + "=" * 70)
    print("Example 2: Detailed Categorization with Reasoning")
    print("=" * 70)
    
    expenses = [
        {"merchant": "Whole Foods Market", "amount": 75.50},
        {"merchant": "Shell Gas Station", "amount": 52.00},
        {"merchant": "Netflix", "amount": 15.99}
    ]
    
    agent = CategorizerAgent()
    categorized = agent.categorize_expenses(expenses, use_llm=False)
    
    print("\nDetailed Results:")
    for item in categorized:
        print(f"\n  Merchant: {item.merchant}")
        print(f"  Amount: ${item.amount:.2f}")
        print(f"  Category: {item.category}")
        print(f"  Confidence: {item.confidence:.0%}")
        print(f"  Reasoning: {item.reasoning}")


def example_all_categories():
    """Example: Show all available categories"""
    print("\n" + "=" * 70)
    print("Example 3: Available Categories")
    print("=" * 70)
    
    agent = CategorizerAgent()
    categories = agent.get_categories()
    
    print(f"\nTotal categories: {len(categories)}")
    print("\nCategories:")
    for cat in categories:
        keywords = agent.CATEGORY_KEYWORDS.get(cat, [])
        print(f"  • {cat:20} (keywords: {len(keywords)})")


def example_merchant_detection():
    """Example: Merchant detection for various merchants"""
    print("\n" + "=" * 70)
    print("Example 4: Merchant Detection")
    print("=" * 70)
    
    merchants = [
        "Starbucks Coffee #123",
        "McDonald's",
        "WHOLE FOODS MARKET",
        "Uber Trip 2024-03-13",
        "Amazon.com Purchase",
        "Netflix Subscription",
        "Shell Oil Company",
        "Best Buy Electronics",
        "CVS Pharmacy",
        "Unknown Store XYZ"
    ]
    
    agent = CategorizerAgent()
    
    print(f"\n{'Merchant':40} {'Category':15} {'Confidence':12}")
    print("-" * 70)
    
    for merchant in merchants:
        expense = {"merchant": merchant, "amount": 0}
        result = agent._categorize_single_keyword(expense)
        if result:
            conf = f"{result.confidence:.0%}"
            print(f"{merchant:40} {result.category:15} {conf:>11}")


def example_batch_processing():
    """Example: Batch processing multiple expenses"""
    print("\n" + "=" * 70)
    print("Example 5: Batch Processing")
    print("=" * 70)
    
    # Simulating a day's expenses
    daily_expenses = [
        {"merchant": "Starbucks", "amount": 5.50},
        {"merchant": "Subway", "amount": 12.00},
        {"merchant": "Shell Gas", "amount": 45.00},
        {"merchant": "Whole Foods", "amount": 67.89},
        {"merchant": "Uber", "amount": 22.50},
        {"merchant": "Netflix", "amount": 15.99},
        {"merchant": "Comcast", "amount": 89.99},
        {"merchant": "CVS Pharmacy", "amount": 18.50},
        {"merchant": "Amazon", "amount": 39.99},
    ]
    
    agent = CategorizerAgent()
    categorized = agent.categorize_expenses(daily_expenses, use_llm=False)
    
    # Group by category
    by_category = {}
    for item in categorized:
        cat = item.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(item)
    
    print(f"\nProcessed {len(categorized)} expenses")
    print("\nExpenses by Category:")
    print("-" * 60)
    
    total = 0
    for category in sorted(by_category.keys()):
        items = by_category[category]
        cat_total = sum(item.amount for item in items)
        total += cat_total
        
        print(f"\n{category.upper()}:")
        for item in items:
            print(f"  {item.merchant:30} ${item.amount:7.2f}")
        print(f"  {'Subtotal':30} ${cat_total:7.2f}")
    
    print("\n" + "-" * 60)
    print(f"{'TOTAL':30} ${total:7.2f}")


def example_custom_categories():
    """Example: Adding custom categories"""
    print("\n" + "=" * 70)
    print("Example 6: Custom Categories")
    print("=" * 70)
    
    agent = CategorizerAgent()
    
    # Add custom category
    agent.add_category("pet", ["vet", "pet store", "petco", "petsmart", "dog", "cat"])
    
    print("Added custom category: 'pet'")
    print(f"Total categories now: {len(agent.get_categories())}")
    
    # Test custom category
    expenses = [
        {"merchant": "Petco Store", "amount": 45.99},
        {"merchant": "Local Vet", "amount": 200.00}
    ]
    
    categorized = agent.categorize_expenses(expenses, use_llm=False)
    
    print("\nCategorized with custom category:")
    for item in categorized:
        print(f"  {item.merchant:20} → {item.category}")


def example_currency_handling():
    """Example: Handle different currencies"""
    print("\n" + "=" * 70)
    print("Example 7: Currency Handling")
    print("=" * 70)
    
    expenses = [
        {"merchant": "Starbucks", "amount": 8.20, "currency": "USD"},
        {"merchant": "Café Paris", "amount": 7.50, "currency": "EUR"},
        {"merchant": "Tesco", "amount": 32.50, "currency": "GBP"},
    ]
    
    agent = CategorizerAgent()
    categorized = agent.categorize_expenses(expenses, use_llm=False)
    
    print(f"\n{'Merchant':20} {'Amount':10} {'Currency':10} {'Category':15}")
    print("-" * 60)
    
    for item in categorized:
        print(f"{item.merchant:20} {item.amount:9.2f}  {item.currency:9} {item.category:15}")


def example_fallback_to_other():
    """Example: Fallback to 'other' category"""
    print("\n" + "=" * 70)
    print("Example 8: Fallback to 'Other' Category")
    print("=" * 70)
    
    # Merchants that don't match common keywords
    unusual_merchants = [
        {"merchant": "Bob's Unknown Shop", "amount": 25.00},
        {"merchant": "XYZ Corporation", "amount": 150.00},
        {"merchant": "Random Store #42", "amount": 10.50},
    ]
    
    agent = CategorizerAgent()
    categorized = agent.categorize_expenses(unusual_merchants, use_llm=False)
    
    print("\nMerchants with no keyword match:")
    print(f"\n{'Merchant':30} {'Category':15} {'Confidence':12}")
    print("-" * 60)
    
    for item in categorized:
        print(f"{item.merchant:30} {item.category:15} {item.confidence:>11.0%}")


def example_confidence_levels():
    """Example: Understanding confidence levels"""
    print("\n" + "=" * 70)
    print("Example 9: Confidence Levels")
    print("=" * 70)
    
    test_merchants = [
        ("Starbucks Coffee", "food"),           # Clear match
        ("Coffee Shop", "food"),                 # Generic match
        ("S", "food"),                          # Single letter
        ("Unknown", "other"),                   # No match
    ]
    
    agent = CategorizerAgent()
    
    print(f"\n{'Merchant':30} {'Category':15} {'Confidence':12} {'Type':20}")
    print("-" * 80)
    
    for merchant, expected_cat in test_merchants:
        expense = {"merchant": merchant, "amount": 10.0}
        result = agent._categorize_single_keyword(expense)
        
        if result:
            conf_type = "Keyword Match" if result.confidence >= 0.7 else "Fallback"
            print(f"{merchant:30} {result.category:15} {result.confidence:>11.0%}  {conf_type:20}")


def example_error_handling():
    """Example: Error handling and edge cases"""
    print("\n" + "=" * 70)
    print("Example 10: Error Handling & Edge Cases")
    print("=" * 70)
    
    unusual_expenses = [
        {"merchant": "Starbucks", "amount": 8.20},
        {"merchant": "", "amount": 10.00},                    # Empty merchant
        {"merchant": "Store"},                                # Missing amount
        {"merchant": "Refund", "amount": -25.00},            # Negative amount
        {"merchant": "Super Expensive Hotel", "amount": 5000.00},  # Large amount
    ]
    
    agent = CategorizerAgent()
    categorized = agent.categorize_expenses(unusual_expenses, use_llm=False)
    
    print(f"\nProcessed {len(categorized)} expenses (some unusual):")
    print(f"\n{'Merchant':30} {'Amount':10} {'Category':15}")
    print("-" * 60)
    
    for item in categorized:
        merchant = item.merchant if item.merchant else "[Empty]"
        print(f"{merchant:30} ${item.amount:9.2f}  {item.category:15}")


def example_integration_with_parser():
    """Example: Integration with receipt parser"""
    print("\n" + "=" * 70)
    print("Example 11: Integration with Receipt Parser")
    print("=" * 70)
    
    # This example shows how categorizer would be used with receipt parser
    
    # 1. Parse receipt text (from previous module)
    receipt_text = """
    Starbucks $8.20
    Whole Foods $45.67
    Uber $22.50
    """
    
    # 2. Simulate parsed expenses
    parsed_expenses = [
        {"merchant": "Starbucks", "amount": 8.20},
        {"merchant": "Whole Foods", "amount": 45.67},
        {"merchant": "Uber", "amount": 22.50}
    ]
    
    print("\nReceipt text:")
    print(receipt_text)
    
    # 3. Categorize
    categorized = categorize_expenses(parsed_expenses, use_llm=False)
    
    print("Categorized expenses:")
    print(f"\n{'Merchant':25} {'Amount':10} {'Category':15}")
    print("-" * 55)
    
    for item in categorized:
        print(f"{item['merchant']:25} ${item['amount']:9.2f}  {item['category']:15}")


def example_json_output():
    """Example: JSON output format"""
    print("\n" + "=" * 70)
    print("Example 12: JSON Output Format")
    print("=" * 70)
    
    import json
    
    expenses = [
        {"merchant": "Starbucks", "amount": 8.20},
        {"merchant": "Uber", "amount": 18.00}
    ]
    
    agent = CategorizerAgent()
    categorized = agent.categorize_expenses(expenses, use_llm=False)
    
    # Convert to JSON
    json_output = json.dumps(
        [item.to_dict() for item in categorized],
        indent=2
    )
    
    print("\nJSON Output:")
    print(json_output)


# Run all examples
if __name__ == "__main__":
    example_simple_categorization()
    example_detailed_categorization()
    example_all_categories()
    example_merchant_detection()
    example_batch_processing()
    example_custom_categories()
    example_currency_handling()
    example_fallback_to_other()
    example_confidence_levels()
    example_error_handling()
    example_integration_with_parser()
    example_json_output()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)
