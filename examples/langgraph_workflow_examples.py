"""
FinSight AI LangGraph Workflow Examples

Demonstrates how to use the FinSight AI workflow in various scenarios.
"""

import json
from datetime import datetime
from src.workflows import FinSightWorkflow


def example_1_text_input():
    """Example 1: Process text receipt directly"""
    print("=" * 60)
    print("Example 1: Process Text Receipt Input")
    print("=" * 60)
    
    # Initialize workflow
    workflow = FinSightWorkflow(use_llm=False, db_path=":memory:")
    
    # Sample receipt text
    receipt_text = """
    Starbucks
    Venti Latte - $6.50
    Croissant - $4.20
    Tax - $0.85
    Total: $11.55
    
    Whole Foods
    Organic Milk - $5.99
    Bread - $4.50
    Vegetables - $12.30
    Tax - $1.80
    Total: $24.59
    
    Uber
    Trip to Downtown - $18.75
    Tax & Fee - $2.25
    Total: $21.00
    """
    
    # Run workflow
    result = workflow.run(
        input_type="text",
        input_content=receipt_text
    )
    
    # Display results
    print(f"\n✅ Workflow Status: {'Complete' if result.is_complete() else 'Failed'}")
    print(f"Processing Time: {result.processing_time_ms:.2f}ms")
    print(f"\n📊 Extracted Text Length: {len(result.extracted_text or '')} characters")
    print(f"📦 Items Found: {len(result.raw_items)}")
    print(f"🏷️ Categorized Expenses: {len(result.categorized_expenses)}")
    
    if result.analysis:
        print(f"\n💰 Financial Analysis:")
        print(f"Total Spending: ${result.analysis.total_spending:.2f}")
        print(f"Expense Count: {result.analysis.expense_count}")
        print(f"\nCategory Breakdown:")
        for cat in result.analysis.category_breakdown:
            print(f"  {cat.category.title()}: ${cat.amount:.2f} ({cat.percentage:.1f}%)")
    
    if result.recommendations:
        print(f"\n💡 Recommendations ({len(result.recommendations)}):")
        for i, rec in enumerate(result.recommendations[:3], 1):
            print(f"  {i}. {rec.title} ({rec.priority})")
            print(f"     Save: ${rec.potential_savings:.2f}/month")
    
    if result.has_error():
        print(f"\n❌ Errors Encountered:")
        for error in result.get_errors():
            print(f"  - {error}")


def example_2_with_budget_limits():
    """Example 2: Run with budget limits"""
    print("\n" + "=" * 60)
    print("Example 2: Workflow with Budget Limits")
    print("=" * 60)
    
    workflow = FinSightWorkflow(use_llm=False, db_path=":memory:")
    
    receipt_text = """
    Amazon
    AirPods Pro - $249.00
    USB Cable - $12.99
    Tax - $20.81
    Total: $282.80
    
    Starbucks
    Cappuccino - $5.50
    Pastry - $5.25
    Tax - $0.85
    Total: $11.60
    
    Gym Membership
    Monthly Fee - $49.99
    """
    
    # Set budget limits
    budgets = {
        "shopping": 100,
        "food": 200,
        "subscriptions": 50
    }
    
    # Run workflow with budgets
    result = workflow.run(
        input_type="text",
        input_content=receipt_text,
        budget_limits=budgets
    )
    
    print(f"\n📋 Budget Limits Set:")
    for cat, limit in budgets.items():
        print(f"  {cat.title()}: ${limit:.2f}")
    
    if result.analysis:
        print(f"\n📊 Budget Analysis:")
        for cat in result.analysis.category_breakdown:
            budget = budgets.get(cat.category)
            if budget:
                if cat.amount > budget:
                    over = cat.amount - budget
                    print(f"  ⚠️  {cat.category.title()}: ${over:.2f} OVER budget")
                else:
                    under = budget - cat.amount
                    print(f"  ✅ {cat.category.title()}: ${under:.2f} under budget")


def example_3_multiple_receipts():
    """Example 3: Process multiple receipts"""
    print("\n" + "=" * 60)
    print("Example 3: Process Multiple Receipts Sequentially")
    print("=" * 60)
    
    workflow = FinSightWorkflow(use_llm=False, db_path=":memory:")
    
    receipts = [
        {
            "name": "Monday - Coffee Shop",
            "text": """
            Starbucks
            Latte - $6.50
            Muffin - $5.99
            Total: $12.49
            """
        },
        {
            "name": "Tuesday - Grocery",
            "text": """
            Whole Foods
            Milk - $5.99
            Eggs - $6.99
            Vegetables - $15.50
            Total: $28.48
            """
        },
        {
            "name": "Wednesday - Transport",
            "text": """
            Uber
            Ride to Airport - $32.50
            Tax & Fee - $5.50
            Total: $38.00
            """
        }
    ]
    
    total_spending = 0
    all_recommendations = []
    
    for receipt in receipts:
        print(f"\n📄 Processing: {receipt['name']}")
        result = workflow.run(input_type="text", input_content=receipt["text"])
        
        if result.analysis:
            total_spending += result.analysis.total_spending
            all_recommendations.extend(result.recommendations)
            print(f"   ✅ ${result.analysis.total_spending:.2f}")
    
    print(f"\n💰 Total Spending: ${total_spending:.2f}")
    print(f"💡 Unique Recommendations: {len(set(r.title for r in all_recommendations))}")


def example_4_json_output():
    """Example 4: Export workflow results as JSON"""
    print("\n" + "=" * 60)
    print("Example 4: JSON Export")
    print("=" * 60)
    
    workflow = FinSightWorkflow(use_llm=False, db_path=":memory:")
    
    receipt_text = """
    Coffee Shop
    Espresso - $3.50
    Croissant - $4.00
    
    Grocery Store
    Milk - $4.99
    Bread - $3.50
    """
    
    result = workflow.run(input_type="text", input_content=receipt_text)
    
    # Convert to dictionary
    state_dict = result.to_dict()
    
    # Pretty print JSON
    print("\n📄 Workflow State as JSON:")
    print(json.dumps(state_dict, indent=2, default=str)[:1000] + "...")
    
    # Save to file
    with open("workflow_result.json", "w") as f:
        json.dump(state_dict, f, indent=2, default=str)
    
    print("\n✅ Full output saved to: workflow_result.json")


def example_5_workflow_diagnostics():
    """Example 5: Inspect workflow errors and diagnostics"""
    print("\n" + "=" * 60)
    print("Example 5: Workflow Diagnostics")
    print("=" * 60)
    
    workflow = FinSightWorkflow(use_llm=False, db_path=":memory:")
    
    # Test with empty input (will fail gracefully)
    result = workflow.run(input_type="text", input_content="")
    
    print(f"\n🔍 Workflow Diagnostics:")
    print(f"Workflow ID: {result.workflow_id}")
    print(f"Created At: {result.created_at}")
    print(f"Completed At: {result.completed_at}")
    print(f"Processing Time: {result.processing_time_ms:.2f}ms")
    print(f"Has Errors: {result.has_error()}")
    
    if result.has_error():
        print(f"\n❌ Errors:")
        for error in result.get_errors():
            print(f"  - {error}")
    
    print(f"\nCompletion Status: {result.is_complete()}")


def example_6_state_inspection():
    """Example 6: Inspect intermediate states"""
    print("\n" + "=" * 60)
    print("Example 6: Intermediate State Inspection")
    print("=" * 60)
    
    workflow = FinSightWorkflow(use_llm=False, db_path=":memory:")
    
    receipt_text = """
    Restaurant ABC
    Burger - $15.99
    Fries - $4.50
    Drink - $3.50
    Tax - $2.50
    Total: $26.49
    """
    
    result = workflow.run(input_type="text", input_content=receipt_text)
    
    print(f"\n📋 Workflow State Snapshots:")
    print(f"\n1️⃣ OCR Output:")
    print(f"   Confidence: {result.ocr_confidence}")
    print(f"   Text Length: {len(result.extracted_text or '')} chars")
    print(f"   Error: {result.ocr_error or 'None'}")
    
    print(f"\n2️⃣ Extraction Output:")
    print(f"   Items Found: {len(result.raw_items)}")
    for item in result.raw_items[:3]:
        print(f"     - {item.merchant}: ${item.amount:.2f}")
    print(f"   Error: {result.extraction_error or 'None'}")
    
    print(f"\n3️⃣ Categorization Output:")
    print(f"   Categorized Items: {len(result.categorized_expenses)}")
    for item in result.categorized_expenses[:3]:
        print(f"     - {item.merchant} ({item.category}): ${item.amount:.2f}")
    print(f"   Error: {result.categorization_error or 'None'}")
    
    print(f"\n4️⃣ Storage Output:")
    print(f"   Storage ID: {result.storage_id or 'Not stored'}")
    print(f"   Error: {result.storage_error or 'None'}")
    
    print(f"\n5️⃣ Analysis Output:")
    if result.analysis:
        print(f"   Total: ${result.analysis.total_spending:.2f}")
        print(f"   Categories: {len(result.analysis.category_breakdown)}")
        print(f"   Highest: {result.analysis.highest_spending_category}")
    print(f"   Error: {result.analysis_error or 'None'}")
    
    print(f"\n6️⃣ Recommendations Output:")
    print(f"   Recommendations: {len(result.recommendations)}")
    for rec in result.recommendations[:2]:
        print(f"     - {rec.title} ({rec.priority})")
    print(f"   Error: {result.recommendation_error or 'None'}")


def example_7_config_comparison():
    """Example 7: Compare keyword vs LLM modes"""
    print("\n" + "=" * 60)
    print("Example 7: Keyword vs LLM Mode Comparison")
    print("=" * 60)
    
    receipt_text = """
    Coffee House
    Specialty Latte - $6.99
    Avocado Toast - $8.50
    
    Rideshare Service
    Trip to Downtown - $22.50
    """
    
    # Keyword mode
    print("\n🔑 Keyword Mode:")
    workflow_keyword = FinSightWorkflow(use_llm=False, db_path=":memory:")
    result_keyword = workflow_keyword.run(input_type="text", input_content=receipt_text)
    
    print(f"Processing Time: {result_keyword.processing_time_ms:.2f}ms")
    if result_keyword.analysis:
        print(f"Total: ${result_keyword.analysis.total_spending:.2f}")
        print(f"Categories: {len(result_keyword.analysis.category_breakdown)}")
    
    # LLM mode (if available)
    print("\n🤖 LLM Mode (if Ollama available):")
    workflow_llm = FinSightWorkflow(use_llm=True, db_path=":memory:")
    result_llm = workflow_llm.run(input_type="text", input_content=receipt_text)
    
    print(f"Processing Time: {result_llm.processing_time_ms:.2f}ms")
    if result_llm.analysis:
        print(f"Total: ${result_llm.analysis.total_spending:.2f}")
        print(f"Categories: {len(result_llm.analysis.category_breakdown)}")
    else:
        print("LLM unavailable - check if Ollama is running")


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("FinSight AI LangGraph Workflow Examples")
    print("🚀" * 30)
    
    # Run all examples
    example_1_text_input()
    example_2_with_budget_limits()
    example_3_multiple_receipts()
    example_4_json_output()
    example_5_workflow_diagnostics()
    example_6_state_inspection()
    example_7_config_comparison()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)
