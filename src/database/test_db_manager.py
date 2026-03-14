"""
Unit tests for FinSight AI SQLite Database Manager Module

Test classes cover:
- Database initialization and table creation
- Expense insertion (single and batch)
- Expense fetching (all, by ID, by date range, by category)
- Monthly total calculations
- Category grouping and analysis
- Summary statistics
- Update and delete operations
- Context manager functionality
"""

import unittest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from src.database.db_manager import DatabaseManager, ExpenseRecord


class TestExpenseRecord(unittest.TestCase):
    """Test ExpenseRecord dataclass."""
    
    def test_expense_record_creation(self):
        """Test creating an expense record with valid data."""
        expense = ExpenseRecord(
            date="2024-03-13",
            merchant="Starbucks",
            category="food",
            amount=6.50,
            notes="Morning coffee"
        )
        
        self.assertEqual(expense.merchant, "Starbucks")
        self.assertEqual(expense.category, "food")
        self.assertEqual(expense.amount, 6.50)
        self.assertIsNone(expense.id)
    
    def test_expense_record_default_date(self):
        """Test that expense record uses current date if not provided."""
        expense = ExpenseRecord(
            merchant="Store",
            category="shopping",
            amount=50.00
        )
        
        today = datetime.now().strftime('%Y-%m-%d')
        self.assertEqual(expense.date, today)
    
    def test_expense_record_to_dict(self):
        """Test converting expense record to dictionary."""
        expense = ExpenseRecord(
            id=1,
            date="2024-03-13",
            merchant="Restaurant",
            category="food",
            amount=25.00,
            notes="Lunch"
        )
        
        expense_dict = expense.to_dict()
        self.assertEqual(expense_dict['id'], 1)
        self.assertEqual(expense_dict['merchant'], "Restaurant")
        self.assertEqual(expense_dict['amount'], 25.00)
    
    def test_expense_record_validation_missing_merchant(self):
        """Test that expense record raises error if merchant is missing."""
        with self.assertRaises(ValueError):
            ExpenseRecord(
                date="2024-03-13",
                merchant="",
                category="food",
                amount=10.00
            )
    
    def test_expense_record_validation_missing_category(self):
        """Test that expense record raises error if category is missing."""
        with self.assertRaises(ValueError):
            ExpenseRecord(
                date="2024-03-13",
                merchant="Store",
                category="",
                amount=10.00
            )
    
    def test_expense_record_validation_negative_amount(self):
        """Test that expense record raises error for negative amount."""
        with self.assertRaises(ValueError):
            ExpenseRecord(
                date="2024-03-13",
                merchant="Store",
                category="shopping",
                amount=-50.00
            )
    
    def test_expense_record_validation_zero_amount(self):
        """Test that expense record raises error for zero amount."""
        with self.assertRaises(ValueError):
            ExpenseRecord(
                date="2024-03-13",
                merchant="Store",
                category="shopping",
                amount=0.0
            )


class TestDatabaseInitialization(unittest.TestCase):
    """Test database initialization and table creation."""
    
    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = DatabaseManager(str(self.db_path))
    
    def tearDown(self):
        """Clean up test database."""
        if self.db:
            self.db.close()
        self.temp_dir.cleanup()
    
    def test_database_creation(self):
        """Test that database file is created."""
        self.assertTrue(self.db_path.exists())
    
    def test_expenses_table_exists(self):
        """Test that expenses table is created."""
        with self.db._get_cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'"
            )
            result = cursor.fetchone()
            self.assertIsNotNone(result)
    
    def test_database_context_manager(self):
        """Test using database manager as context manager."""
        with DatabaseManager(str(self.db_path)) as db:
            self.assertIsNotNone(db.connection)


class TestExpenseInsertion(unittest.TestCase):
    """Test inserting expenses into database."""
    
    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = DatabaseManager(str(self.db_path))
    
    def tearDown(self):
        """Clean up test database."""
        if self.db:
            self.db.close()
        self.temp_dir.cleanup()
    
    def test_insert_single_expense(self):
        """Test inserting a single expense."""
        expense = ExpenseRecord(
            date="2024-03-13",
            merchant="Starbucks",
            category="food",
            amount=6.50
        )
        
        expense_id = self.db.insert_expense(expense)
        self.assertIsNotNone(expense_id)
        self.assertGreater(expense_id, 0)
    
    def test_insert_multiple_expenses(self):
        """Test inserting multiple expenses."""
        expenses = [
            ExpenseRecord(date="2024-03-13", merchant="Store1", category="shopping", amount=50.00),
            ExpenseRecord(date="2024-03-14", merchant="Restaurant", category="food", amount=25.00),
            ExpenseRecord(date="2024-03-15", merchant="Gas", category="transport", amount=45.00),
        ]
        
        for expense in expenses:
            self.db.insert_expense(expense)
        
        all_expenses = self.db.fetch_all_expenses()
        self.assertEqual(len(all_expenses), 3)
    
    def test_insert_expenses_batch(self):
        """Test batch inserting expenses."""
        expenses = [
            ExpenseRecord(date="2024-03-13", merchant="Store1", category="shopping", amount=50.00),
            ExpenseRecord(date="2024-03-14", merchant="Restaurant", category="food", amount=25.00),
            ExpenseRecord(date="2024-03-15", merchant="Gas", category="transport", amount=45.00),
        ]
        
        ids = self.db.insert_expenses_batch(expenses)
        
        self.assertEqual(len(ids), 3)
        self.assertTrue(all(isinstance(id, int) for id in ids))


class TestExpenseFetching(unittest.TestCase):
    """Test fetching expenses from database."""
    
    def setUp(self):
        """Create a temporary database with test data."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = DatabaseManager(str(self.db_path))
        
        # Insert test data
        self.test_expenses = [
            ExpenseRecord(date="2024-03-01", merchant="Coffee Shop", category="food", amount=5.00),
            ExpenseRecord(date="2024-03-05", merchant="Grocery", category="food", amount=50.00),
            ExpenseRecord(date="2024-03-10", merchant="Gas Station", category="transport", amount=40.00),
            ExpenseRecord(date="2024-03-15", merchant="Target", category="shopping", amount=75.00),
            ExpenseRecord(date="2024-03-20", merchant="Restaurant", category="food", amount=30.00),
        ]
        
        for expense in self.test_expenses:
            self.db.insert_expense(expense)
    
    def tearDown(self):
        """Clean up test database."""
        if self.db:
            self.db.close()
        self.temp_dir.cleanup()
    
    def test_fetch_all_expenses(self):
        """Test fetching all expenses."""
        expenses = self.db.fetch_all_expenses()
        self.assertEqual(len(expenses), 5)
    
    def test_fetch_expense_by_id(self):
        """Test fetching expense by ID."""
        # Get first expense
        all_expenses = self.db.fetch_all_expenses()
        first_id = all_expenses[0].id
        
        expense = self.db.fetch_expense_by_id(first_id)
        self.assertIsNotNone(expense)
        self.assertEqual(expense.id, first_id)
    
    def test_fetch_nonexistent_expense(self):
        """Test fetching non-existent expense returns None."""
        expense = self.db.fetch_expense_by_id(9999)
        self.assertIsNone(expense)
    
    def test_fetch_expenses_by_date_range(self):
        """Test fetching expenses within a date range."""
        expenses = self.db.fetch_expenses_by_date_range("2024-03-05", "2024-03-15")
        self.assertEqual(len(expenses), 3)  # 5th, 10th, 15th
    
    def test_fetch_expenses_by_category(self):
        """Test fetching expenses by category."""
        food_expenses = self.db.fetch_expenses_by_category("food")
        self.assertEqual(len(food_expenses), 3)  # Coffee, Grocery, Restaurant
        
        total = sum(e.amount for e in food_expenses)
        self.assertEqual(total, 85.00)
    
    def test_fetch_expenses_invalid_date_format(self):
        """Test that invalid date format raises ValueError."""
        with self.assertRaises(ValueError):
            self.db.fetch_expenses_by_date_range("2024/03/05", "2024/03/15")


class TestMonthlyTotals(unittest.TestCase):
    """Test monthly total calculations."""
    
    def setUp(self):
        """Create a temporary database with test data."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = DatabaseManager(str(self.db_path))
        
        # Insert test data across multiple months
        expenses = [
            ExpenseRecord(date="2024-01-10", merchant="Store", category="shopping", amount=100.00),
            ExpenseRecord(date="2024-01-15", merchant="Restaurant", category="food", amount=50.00),
            ExpenseRecord(date="2024-02-05", merchant="Gas", category="transport", amount=40.00),
            ExpenseRecord(date="2024-02-20", merchant="Grocery", category="food", amount=60.00),
            ExpenseRecord(date="2024-03-01", merchant="Coffee", category="food", amount=5.00),
            ExpenseRecord(date="2024-03-15", merchant="Target", category="shopping", amount=75.00),
        ]
        
        for expense in expenses:
            self.db.insert_expense(expense)
    
    def tearDown(self):
        """Clean up test database."""
        if self.db:
            self.db.close()
        self.temp_dir.cleanup()
    
    def test_calculate_monthly_totals_all_months(self):
        """Test calculating totals for all months in a year."""
        totals = self.db.calculate_monthly_totals(year=2024)
        
        self.assertEqual(len(totals), 3)  # 3 months with expenses
        self.assertEqual(totals['2024-01'], 150.00)  # 100 + 50
        self.assertEqual(totals['2024-02'], 100.00)  # 40 + 60
        self.assertEqual(totals['2024-03'], 80.00)   # 5 + 75
    
    def test_calculate_monthly_totals_specific_month(self):
        """Test calculating total for a specific month."""
        totals = self.db.calculate_monthly_totals(year=2024, month=2)
        
        self.assertEqual(len(totals), 1)
        self.assertEqual(totals['2024-02'], 100.00)
    
    def test_calculate_monthly_totals_invalid_month(self):
        """Test that invalid month raises ValueError."""
        with self.assertRaises(ValueError):
            self.db.calculate_monthly_totals(year=2024, month=13)


class TestCategoryGrouping(unittest.TestCase):
    """Test grouping expenses by category."""
    
    def setUp(self):
        """Create a temporary database with test data."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = DatabaseManager(str(self.db_path))
        
        # Insert test data
        expenses = [
            ExpenseRecord(date="2024-03-01", merchant="Coffee", category="food", amount=5.00),
            ExpenseRecord(date="2024-03-05", merchant="Grocery", category="food", amount=50.00),
            ExpenseRecord(date="2024-03-10", merchant="Restaurant", category="food", amount=30.00),
            ExpenseRecord(date="2024-03-15", merchant="Gas", category="transport", amount=40.00),
            ExpenseRecord(date="2024-03-20", merchant="Target", category="shopping", amount=100.00),
        ]
        
        for expense in expenses:
            self.db.insert_expense(expense)
    
    def tearDown(self):
        """Clean up test database."""
        if self.db:
            self.db.close()
        self.temp_dir.cleanup()
    
    def test_group_expenses_by_category(self):
        """Test grouping expenses by category."""
        grouped = self.db.group_expenses_by_category()
        
        self.assertEqual(len(grouped), 3)  # 3 categories
        
        # Check food category
        self.assertIn('food', grouped)
        self.assertEqual(grouped['food']['count'], 3)
        self.assertEqual(grouped['food']['total'], 85.00)
        self.assertAlmostEqual(grouped['food']['average'], 28.33, places=1)
        
        # Check shopping category
        self.assertIn('shopping', grouped)
        self.assertEqual(grouped['shopping']['count'], 1)
        self.assertEqual(grouped['shopping']['total'], 100.00)
    
    def test_category_percentages(self):
        """Test that category percentages are calculated correctly."""
        grouped = self.db.group_expenses_by_category()
        
        # Total should be 225 (85 + 40 + 100)
        self.assertAlmostEqual(grouped['food']['percentage'], 37.78, places=1)
        self.assertAlmostEqual(grouped['transport']['percentage'], 17.78, places=1)
        self.assertAlmostEqual(grouped['shopping']['percentage'], 44.44, places=1)
    
    def test_category_expenses_list(self):
        """Test that category grouping includes individual expenses."""
        grouped = self.db.group_expenses_by_category()
        
        food_expenses = grouped['food']['expenses']
        self.assertEqual(len(food_expenses), 3)


class TestSummaryStatistics(unittest.TestCase):
    """Test summary statistics calculation."""
    
    def setUp(self):
        """Create a temporary database with test data."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = DatabaseManager(str(self.db_path))
        
        # Insert test data
        expenses = [
            ExpenseRecord(date="2024-03-01", merchant="Store", category="shopping", amount=10.00),
            ExpenseRecord(date="2024-03-05", merchant="Restaurant", category="food", amount=50.00),
            ExpenseRecord(date="2024-03-10", merchant="Gas", category="transport", amount=40.00),
            ExpenseRecord(date="2024-03-15", merchant="Coffee", category="food", amount=5.00),
        ]
        
        for expense in expenses:
            self.db.insert_expense(expense)
    
    def tearDown(self):
        """Clean up test database."""
        if self.db:
            self.db.close()
        self.temp_dir.cleanup()
    
    def test_summary_statistics(self):
        """Test getting summary statistics."""
        stats = self.db.get_summary_statistics()
        
        self.assertEqual(stats['total_expenses'], 4)
        self.assertEqual(stats['total_spending'], 105.00)
        self.assertAlmostEqual(stats['average_expense'], 26.25, places=2)
        self.assertEqual(stats['max_expense'], 50.00)
        self.assertEqual(stats['min_expense'], 5.00)
        self.assertEqual(stats['categories_count'], 3)
    
    def test_summary_statistics_date_range(self):
        """Test that date range is included in statistics."""
        stats = self.db.get_summary_statistics()
        
        self.assertIn('date_range', stats)
        self.assertEqual(stats['date_range']['start'], '2024-03-01')
        self.assertEqual(stats['date_range']['end'], '2024-03-15')
    
    def test_summary_statistics_empty_database(self):
        """Test summary statistics with empty database."""
        # Create new database without data
        temp_dir = tempfile.TemporaryDirectory()
        db_path = Path(temp_dir.name) / "empty.db"
        db = DatabaseManager(str(db_path))
        
        stats = db.get_summary_statistics()
        
        self.assertEqual(stats['total_expenses'], 0)
        self.assertEqual(stats['total_spending'], 0)
        
        db.close()
        temp_dir.cleanup()


class TestUpdateAndDelete(unittest.TestCase):
    """Test updating and deleting expenses."""
    
    def setUp(self):
        """Create a temporary database with test data."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        self.db = DatabaseManager(str(self.db_path))
        
        # Insert test expense
        self.expense = ExpenseRecord(
            date="2024-03-13",
            merchant="Starbucks",
            category="food",
            amount=6.50
        )
        self.expense_id = self.db.insert_expense(self.expense)
    
    def tearDown(self):
        """Clean up test database."""
        if self.db:
            self.db.close()
        self.temp_dir.cleanup()
    
    def test_update_expense(self):
        """Test updating an expense."""
        success = self.db.update_expense(self.expense_id, amount=7.50, notes="Updated")
        
        self.assertTrue(success)
        
        updated = self.db.fetch_expense_by_id(self.expense_id)
        self.assertEqual(updated.amount, 7.50)
        self.assertEqual(updated.notes, "Updated")
    
    def test_update_nonexistent_expense(self):
        """Test that updating non-existent expense raises ValueError."""
        with self.assertRaises(ValueError):
            self.db.update_expense(9999, amount=10.00)
    
    def test_delete_expense(self):
        """Test deleting an expense."""
        success = self.db.delete_expense(self.expense_id)
        
        self.assertTrue(success)
        
        deleted = self.db.fetch_expense_by_id(self.expense_id)
        self.assertIsNone(deleted)
    
    def test_delete_nonexistent_expense(self):
        """Test that deleting non-existent expense raises ValueError."""
        with self.assertRaises(ValueError):
            self.db.delete_expense(9999)
    
    def test_delete_all_expenses(self):
        """Test deleting all expenses."""
        self.db.insert_expense(ExpenseRecord(
            date="2024-03-14",
            merchant="Restaurant",
            category="food",
            amount=25.00
        ))
        
        count = self.db.delete_all_expenses()
        
        self.assertEqual(count, 2)
        
        all_expenses = self.db.fetch_all_expenses()
        self.assertEqual(len(all_expenses), 0)


if __name__ == '__main__':
    unittest.main()
