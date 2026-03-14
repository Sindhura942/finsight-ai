"""
FinSight AI Database Module - Usage Examples

This file contains practical examples demonstrating how to use the
DatabaseManager class for common expense tracking tasks.

Examples include:
1. Basic usage and setup
2. Inserting expenses
3. Fetching expenses
4. Calculating monthly totals
5. Analyzing expenses by category
6. Generating reports
7. Updating and deleting expenses
"""

from src.database.db_manager import DatabaseManager, ExpenseRecord
from datetime import datetime, timedelta


def example_1_basic_setup():
    """
    Example 1: Basic setup and creating a database connection.
    
    Shows how to initialize the database manager and verify it's working.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Setup")
    print("="*60)
    
    # Initialize database manager (creates database if it doesn't exist)
    db = DatabaseManager("finsight_expenses.db")
    print(f"✓ Database initialized at finsight_expenses.db")
    
    # Using context manager (automatically closes connection)
    with DatabaseManager("finsight_expenses.db") as db:
        print("✓ Using context manager for automatic cleanup")
    
    db.close()
    print("✓ Database connection closed")


def example_2_inserting_single_expense():
    """
    Example 2: Inserting a single expense record.
    
    Shows how to create an ExpenseRecord and insert it into the database.
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Inserting Single Expense")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        # Create an expense record
        expense = ExpenseRecord(
            date="2024-03-13",
            merchant="Starbucks",
            category="food & dining",
            amount=6.50,
            notes="Morning coffee"
        )
        
        # Insert into database
        expense_id = db.insert_expense(expense)
        print(f"✓ Expense inserted with ID: {expense_id}")
        print(f"  Merchant: {expense.merchant}")
        print(f"  Amount: ${expense.amount:.2f}")
        print(f"  Category: {expense.category}")


def example_3_batch_inserting_expenses():
    """
    Example 3: Inserting multiple expenses at once.
    
    Shows how to batch insert multiple expense records efficiently.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Batch Inserting Expenses")
    print("="*60)
    
    # Create multiple expense records
    expenses = [
        ExpenseRecord(
            date="2024-03-13",
            merchant="Whole Foods",
            category="groceries",
            amount=75.50,
            notes="Weekly groceries"
        ),
        ExpenseRecord(
            date="2024-03-14",
            merchant="Shell Gas Station",
            category="transportation",
            amount=45.00,
            notes="Fuel"
        ),
        ExpenseRecord(
            date="2024-03-14",
            merchant="Target",
            category="shopping",
            amount=120.00,
            notes="Household items"
        ),
        ExpenseRecord(
            date="2024-03-15",
            merchant="Chipotle",
            category="food & dining",
            amount=12.50,
            notes="Lunch"
        ),
    ]
    
    with DatabaseManager("finsight_expenses.db") as db:
        # Batch insert all expenses
        ids = db.insert_expenses_batch(expenses)
        print(f"✓ Inserted {len(ids)} expenses in batch mode")
        for i, expense_id in enumerate(ids):
            print(f"  {i+1}. {expenses[i].merchant} - ${expenses[i].amount:.2f} (ID: {expense_id})")


def example_4_fetching_all_expenses():
    """
    Example 4: Fetching all expenses from the database.
    
    Shows how to retrieve all expense records with different sorting options.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Fetching All Expenses")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        # Fetch all expenses (ordered by date, newest first)
        expenses = db.fetch_all_expenses(order_by="date DESC")
        
        print(f"✓ Retrieved {len(expenses)} expenses\n")
        print(f"{'Date':<12} {'Merchant':<20} {'Category':<18} {'Amount':>10}")
        print("-" * 60)
        
        for expense in expenses:
            print(f"{expense.date}  {expense.merchant:<20} {expense.category:<18} ${expense.amount:>9.2f}")


def example_5_fetching_by_date_range():
    """
    Example 5: Fetching expenses within a date range.
    
    Shows how to retrieve expenses between two dates.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Fetching by Date Range")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        # Fetch expenses from March 1-15, 2024
        expenses = db.fetch_expenses_by_date_range("2024-03-01", "2024-03-15")
        
        print(f"✓ Expenses from 2024-03-01 to 2024-03-15: {len(expenses)}")
        total = sum(e.amount for e in expenses)
        print(f"  Total spent: ${total:.2f}")


def example_6_fetching_by_category():
    """
    Example 6: Fetching expenses by category.
    
    Shows how to retrieve all expenses in a specific category.
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Fetching by Category")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        # Fetch all food & dining expenses
        food_expenses = db.fetch_expenses_by_category("food & dining")
        
        print(f"✓ Food & Dining Expenses: {len(food_expenses)}")
        total = sum(e.amount for e in food_expenses)
        avg = total / len(food_expenses) if food_expenses else 0
        
        print(f"  Total: ${total:.2f}")
        print(f"  Average per transaction: ${avg:.2f}\n")
        
        for expense in food_expenses:
            print(f"  - {expense.date}: {expense.merchant} - ${expense.amount:.2f}")


def example_7_monthly_totals():
    """
    Example 7: Calculating monthly spending totals.
    
    Shows how to get total spending broken down by month.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Monthly Spending Totals")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        # Get all monthly totals for 2024
        monthly_totals = db.calculate_monthly_totals(year=2024)
        
        print("✓ Monthly Totals for 2024:\n")
        
        if not monthly_totals:
            print("  No expenses found for 2024")
        else:
            total_year = sum(monthly_totals.values())
            for month, total in sorted(monthly_totals.items()):
                percentage = (total / total_year * 100) if total_year > 0 else 0
                print(f"  {month}: ${total:>8.2f} ({percentage:>5.1f}%)")
            print(f"  {'─' * 30}")
            print(f"  Year Total: ${total_year:.2f}")


def example_8_category_analysis():
    """
    Example 8: Analyzing expenses by category.
    
    Shows how to get comprehensive category breakdown including
    count, total, average, percentage, and individual expenses.
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: Category Analysis")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        grouped = db.group_expenses_by_category()
        
        print("✓ Expenses by Category:\n")
        print(f"{'Category':<20} {'Count':>6} {'Total':>10} {'Average':>10} {'%':>6}")
        print("-" * 52)
        
        for category, data in sorted(
            grouped.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        ):
            print(
                f"{category:<20} {data['count']:>6} "
                f"${data['total']:>9.2f} ${data['average']:>9.2f} "
                f"{data['percentage']:>5.1f}%"
            )
        
        # Show top expense in each category
        print("\n✓ Highest Expense per Category:\n")
        for category, data in grouped.items():
            if data['expenses']:
                highest = max(data['expenses'], key=lambda x: x['amount'])
                print(f"  {category}: {highest['merchant']} (${highest['amount']:.2f})")


def example_9_summary_statistics():
    """
    Example 9: Getting summary statistics.
    
    Shows how to get overall statistics about all expenses.
    """
    print("\n" + "="*60)
    print("EXAMPLE 9: Summary Statistics")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        stats = db.get_summary_statistics()
        
        print("✓ Overall Statistics:\n")
        print(f"  Total Expenses:    {stats['total_expenses']}")
        print(f"  Total Spending:    ${stats['total_spending']:.2f}")
        print(f"  Average Expense:   ${stats['average_expense']:.2f}")
        print(f"  Highest Expense:   ${stats['max_expense']:.2f}")
        print(f"  Lowest Expense:    ${stats['min_expense']:.2f}")
        print(f"  Categories:        {stats['categories_count']}")
        
        if stats['date_range']['start']:
            print(f"\n  Date Range:")
            print(f"    From: {stats['date_range']['start']}")
            print(f"    To:   {stats['date_range']['end']}")


def example_10_updating_expenses():
    """
    Example 10: Updating existing expenses.
    
    Shows how to modify expense records in the database.
    """
    print("\n" + "="*60)
    print("EXAMPLE 10: Updating Expenses")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        # Get first expense
        all_expenses = db.fetch_all_expenses()
        
        if all_expenses:
            expense = all_expenses[0]
            print(f"✓ Original expense (ID: {expense.id}):")
            print(f"  Merchant: {expense.merchant}")
            print(f"  Amount: ${expense.amount:.2f}")
            print(f"  Notes: {expense.notes}")
            
            # Update the expense
            db.update_expense(
                expense.id,
                amount=8.75,
                notes="Updated - corrected amount"
            )
            
            # Fetch and display updated expense
            updated = db.fetch_expense_by_id(expense.id)
            print(f"\n✓ Updated expense (ID: {updated.id}):")
            print(f"  Merchant: {updated.merchant}")
            print(f"  Amount: ${updated.amount:.2f}")
            print(f"  Notes: {updated.notes}")
        else:
            print("No expenses to update")


def example_11_deleting_expenses():
    """
    Example 11: Deleting expenses.
    
    Shows how to remove expense records from the database.
    """
    print("\n" + "="*60)
    print("EXAMPLE 11: Deleting Expenses")
    print("="*60)
    
    with DatabaseManager("finsight_expenses.db") as db:
        # Get all expenses
        all_expenses = db.fetch_all_expenses()
        print(f"✓ Total expenses before: {len(all_expenses)}")
        
        if all_expenses:
            # Delete the last expense
            expense_to_delete = all_expenses[-1]
            print(f"\n  Deleting: {expense_to_delete.merchant} "
                  f"(${expense_to_delete.amount:.2f})")
            
            db.delete_expense(expense_to_delete.id)
            
            # Verify deletion
            remaining = db.fetch_all_expenses()
            print(f"\n✓ Total expenses after: {len(remaining)}")


def example_12_budget_analysis():
    """
    Example 12: Analyzing budget vs actual spending.
    
    Shows how to use the database to track spending against budgets.
    """
    print("\n" + "="*60)
    print("EXAMPLE 12: Budget Analysis")
    print("="*60)
    
    # Define monthly budget
    budget = {
        "food & dining": 300.00,
        "transportation": 200.00,
        "shopping": 500.00,
        "groceries": 400.00,
    }
    
    with DatabaseManager("finsight_expenses.db") as db:
        grouped = db.group_expenses_by_category()
        
        print("✓ Budget vs Actual (March 2024):\n")
        print(f"{'Category':<20} {'Budget':>10} {'Actual':>10} {'Remaining':>10} {'Status':>8}")
        print("-" * 58)
        
        for category, budgeted_amount in sorted(budget.items()):
            actual = grouped.get(category, {}).get('total', 0)
            remaining = budgeted_amount - actual
            
            if remaining >= 0:
                status = "✓ OK"
            else:
                status = "✗ OVER"
            
            print(
                f"{category:<20} ${budgeted_amount:>9.2f} "
                f"${actual:>9.2f} ${remaining:>9.2f} {status:>8}"
            )


def run_all_examples():
    """
    Run all examples in sequence.
    
    This function demonstrates the complete workflow of using the
    database manager for expense tracking.
    """
    print("\n" + "="*60)
    print("FINSIGHT AI - DATABASE MODULE EXAMPLES")
    print("="*60)
    
    try:
        example_1_basic_setup()
        example_2_inserting_single_expense()
        example_3_batch_inserting_expenses()
        example_4_fetching_all_expenses()
        example_5_fetching_by_date_range()
        example_6_fetching_by_category()
        example_7_monthly_totals()
        example_8_category_analysis()
        example_9_summary_statistics()
        example_10_updating_expenses()
        example_11_deleting_expenses()
        example_12_budget_analysis()
        
        print("\n" + "="*60)
        print("✓ All examples completed successfully!")
        print("="*60 + "\n")
    
    except Exception as e:
        print(f"\n✗ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
