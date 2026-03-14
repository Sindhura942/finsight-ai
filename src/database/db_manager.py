"""
FinSight AI - SQLite Database Manager Module

This module provides database management functionality for FinSight AI,
including operations for expenses tracking, querying, and analysis.

Classes:
    DatabaseManager: Main class for database operations
    ExpenseRecord: Data class for expense records

Functions:
    create_connection: Create database connection
    close_connection: Close database connection
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass, field
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


@dataclass
class ExpenseRecord:
    """
    Data class representing an expense record.
    
    Attributes:
        id: Unique expense identifier (auto-generated)
        date: Date of the expense (YYYY-MM-DD)
        merchant: Name of the merchant/vendor
        category: Expense category (e.g., 'food', 'transportation')
        amount: Expense amount in dollars
        created_at: Timestamp when record was created (auto-generated)
        notes: Optional notes about the expense
    """
    id: Optional[int] = None
    date: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'))
    merchant: str = ""
    category: str = ""
    amount: float = 0.0
    created_at: Optional[str] = None
    notes: str = ""
    
    def __post_init__(self):
        """Validate expense record data."""
        if not self.date:
            self.date = datetime.now().strftime('%Y-%m-%d')
        if not self.merchant:
            raise ValueError("Merchant name is required")
        if not self.category:
            raise ValueError("Category is required")
        if self.amount <= 0:
            raise ValueError("Amount must be greater than 0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert expense record to dictionary."""
        return {
            'id': self.id,
            'date': self.date,
            'merchant': self.merchant,
            'category': self.category,
            'amount': self.amount,
            'created_at': self.created_at,
            'notes': self.notes
        }
    
    def __repr__(self) -> str:
        """String representation of expense record."""
        return (
            f"ExpenseRecord(id={self.id}, date={self.date}, "
            f"merchant={self.merchant}, category={self.category}, "
            f"amount=${self.amount:.2f})"
        )


class DatabaseManager:
    """
    Manages SQLite database operations for FinSight AI.
    
    Provides functionality for:
    - Creating and managing the expenses table
    - Inserting expense records
    - Fetching expense data
    - Calculating monthly totals
    - Grouping expenses by category
    - Querying with filters
    
    Attributes:
        db_path: Path to SQLite database file
        connection: SQLite connection object
    """
    
    def __init__(self, db_path: str = "finsight_expenses.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file (default: finsight_expenses.db)
        
        Raises:
            Exception: If database initialization fails
        """
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        
        try:
            self.connection = self._create_connection()
            logger.info(f"Database initialized at {self.db_path}")
            self._create_tables()
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def _create_connection(self) -> sqlite3.Connection:
        """
        Create connection to SQLite database.
        
        Returns:
            sqlite3.Connection: Database connection object
        
        Raises:
            sqlite3.Error: If connection fails
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            # Set row factory to return dictionaries
            conn.row_factory = sqlite3.Row
            logger.debug(f"Connection established to {self.db_path}")
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    def _create_tables(self) -> None:
        """
        Create database tables if they don't exist.
        
        Creates:
        - expenses: Main expenses table with all required columns
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")
        
        create_expenses_table = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            merchant TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CHECK(amount > 0),
            CHECK(length(date) = 10 AND date LIKE '____-__-__')
        )
        """
        
        try:
            self.connection.execute(create_expenses_table)
            self.connection.commit()
            logger.info("Expenses table created/verified")
        except sqlite3.Error as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
    
    @contextmanager
    def _get_cursor(self):
        """
        Context manager for database cursor.
        
        Yields:
            sqlite3.Cursor: Database cursor
        """
        if not self.connection:
            raise RuntimeError("Database connection not established")
        
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            cursor.close()
    
    def insert_expense(self, expense: ExpenseRecord) -> int:
        """
        Insert a new expense record into the database.
        
        Args:
            expense: ExpenseRecord object with expense data
        
        Returns:
            int: ID of inserted expense
        
        Raises:
            ValueError: If expense data is invalid
            sqlite3.Error: If database operation fails
        
        Example:
            >>> expense = ExpenseRecord(
            ...     date="2024-03-13",
            ...     merchant="Starbucks",
            ...     category="food",
            ...     amount=6.50,
            ...     notes="Morning coffee"
            ... )
            >>> db = DatabaseManager()
            >>> expense_id = db.insert_expense(expense)
            >>> print(f"Inserted expense with ID: {expense_id}")
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO expenses 
                    (date, merchant, category, amount, notes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        expense.date,
                        expense.merchant,
                        expense.category,
                        expense.amount,
                        expense.notes
                    )
                )
                expense_id = cursor.lastrowid
                logger.info(
                    f"Inserted expense: {expense.merchant} "
                    f"${expense.amount:.2f} (ID: {expense_id})"
                )
                return expense_id
        except sqlite3.Error as e:
            logger.error(f"Failed to insert expense: {str(e)}")
            raise
    
    def insert_expenses_batch(self, expenses: List[ExpenseRecord]) -> List[int]:
        """
        Insert multiple expense records in batch mode.
        
        Args:
            expenses: List of ExpenseRecord objects
        
        Returns:
            List[int]: IDs of inserted expenses
        
        Raises:
            ValueError: If any expense data is invalid
            sqlite3.Error: If database operation fails
        
        Example:
            >>> expenses = [
            ...     ExpenseRecord(date="2024-03-13", merchant="Store1", 
            ...                   category="shopping", amount=50.00),
            ...     ExpenseRecord(date="2024-03-14", merchant="Restaurant", 
            ...                   category="food", amount=25.00),
            ... ]
            >>> db = DatabaseManager()
            >>> ids = db.insert_expenses_batch(expenses)
            >>> print(f"Inserted {len(ids)} expenses")
        """
        try:
            with self._get_cursor() as cursor:
                expense_ids = []
                for expense in expenses:
                    cursor.execute(
                        """
                        INSERT INTO expenses 
                        (date, merchant, category, amount, notes)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            expense.date,
                            expense.merchant,
                            expense.category,
                            expense.amount,
                            expense.notes
                        )
                    )
                    expense_ids.append(cursor.lastrowid)
                
                logger.info(f"Batch inserted {len(expense_ids)} expenses")
                return expense_ids
        except sqlite3.Error as e:
            logger.error(f"Failed to insert expenses batch: {str(e)}")
            raise
    
    def fetch_all_expenses(self, order_by: str = "date DESC") -> List[ExpenseRecord]:
        """
        Fetch all expenses from the database.
        
        Args:
            order_by: SQL ORDER BY clause (default: "date DESC")
        
        Returns:
            List[ExpenseRecord]: List of all expense records
        
        Raises:
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> expenses = db.fetch_all_expenses()
            >>> for expense in expenses:
            ...     print(f"{expense.date} - {expense.merchant}: ${expense.amount:.2f}")
        """
        try:
            with self._get_cursor() as cursor:
                query = f"SELECT * FROM expenses ORDER BY {order_by}"
                cursor.execute(query)
                rows = cursor.fetchall()
                
                expenses = [
                    ExpenseRecord(
                        id=row['id'],
                        date=row['date'],
                        merchant=row['merchant'],
                        category=row['category'],
                        amount=row['amount'],
                        created_at=row['created_at'],
                        notes=row['notes']
                    )
                    for row in rows
                ]
                
                logger.debug(f"Fetched {len(expenses)} expenses")
                return expenses
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch expenses: {str(e)}")
            raise
    
    def fetch_expense_by_id(self, expense_id: int) -> Optional[ExpenseRecord]:
        """
        Fetch a specific expense by ID.
        
        Args:
            expense_id: ID of the expense to fetch
        
        Returns:
            ExpenseRecord if found, None otherwise
        
        Raises:
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> expense = db.fetch_expense_by_id(1)
            >>> if expense:
            ...     print(f"Found: {expense.merchant} - ${expense.amount:.2f}")
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM expenses WHERE id = ?",
                    (expense_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    logger.debug(f"Expense with ID {expense_id} not found")
                    return None
                
                expense = ExpenseRecord(
                    id=row['id'],
                    date=row['date'],
                    merchant=row['merchant'],
                    category=row['category'],
                    amount=row['amount'],
                    created_at=row['created_at'],
                    notes=row['notes']
                )
                
                logger.debug(f"Fetched expense ID {expense_id}")
                return expense
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch expense: {str(e)}")
            raise
    
    def fetch_expenses_by_date_range(
        self,
        start_date: str,
        end_date: str
    ) -> List[ExpenseRecord]:
        """
        Fetch expenses within a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
        
        Returns:
            List[ExpenseRecord]: Expenses within the date range
        
        Raises:
            ValueError: If date format is invalid
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> expenses = db.fetch_expenses_by_date_range("2024-03-01", "2024-03-31")
            >>> print(f"Found {len(expenses)} expenses in March 2024")
        """
        try:
            # Validate date format
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
            
            with self._get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM expenses 
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                    """,
                    (start_date, end_date)
                )
                rows = cursor.fetchall()
                
                expenses = [
                    ExpenseRecord(
                        id=row['id'],
                        date=row['date'],
                        merchant=row['merchant'],
                        category=row['category'],
                        amount=row['amount'],
                        created_at=row['created_at'],
                        notes=row['notes']
                    )
                    for row in rows
                ]
                
                logger.debug(
                    f"Fetched {len(expenses)} expenses from "
                    f"{start_date} to {end_date}"
                )
                return expenses
        except ValueError as e:
            logger.error(f"Invalid date format: {str(e)}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch expenses by date range: {str(e)}")
            raise
    
    def fetch_expenses_by_category(self, category: str) -> List[ExpenseRecord]:
        """
        Fetch all expenses in a specific category.
        
        Args:
            category: Expense category to filter by
        
        Returns:
            List[ExpenseRecord]: Expenses in the specified category
        
        Raises:
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> food_expenses = db.fetch_expenses_by_category("food")
            >>> total = sum(e.amount for e in food_expenses)
            >>> print(f"Total food spending: ${total:.2f}")
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM expenses 
                    WHERE category = ?
                    ORDER BY date DESC
                    """,
                    (category,)
                )
                rows = cursor.fetchall()
                
                expenses = [
                    ExpenseRecord(
                        id=row['id'],
                        date=row['date'],
                        merchant=row['merchant'],
                        category=row['category'],
                        amount=row['amount'],
                        created_at=row['created_at'],
                        notes=row['notes']
                    )
                    for row in rows
                ]
                
                logger.debug(
                    f"Fetched {len(expenses)} expenses in category '{category}'"
                )
                return expenses
        except sqlite3.Error as e:
            logger.error(f"Failed to fetch expenses by category: {str(e)}")
            raise
    
    def calculate_monthly_totals(self, year: int = None, month: int = None) -> Dict[str, float]:
        """
        Calculate total spending by month.
        
        Args:
            year: Year to filter by (default: current year)
            month: Month to filter by (default: all months)
        
        Returns:
            Dict[str, float]: Dictionary with month as key and total as value
        
        Raises:
            ValueError: If year or month is invalid
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> totals = db.calculate_monthly_totals(year=2024, month=3)
            >>> print(f"March 2024 total: ${totals['2024-03']:.2f}")
            
            >>> all_totals = db.calculate_monthly_totals(year=2024)
            >>> for month_str, total in all_totals.items():
            ...     print(f"{month_str}: ${total:.2f}")
        """
        try:
            if year is None:
                year = datetime.now().year
            if year < 2000 or year > 2100:
                raise ValueError(f"Invalid year: {year}")
            if month is not None and (month < 1 or month > 12):
                raise ValueError(f"Invalid month: {month}")
            
            with self._get_cursor() as cursor:
                if month is not None:
                    # Specific month
                    cursor.execute(
                        """
                        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
                        FROM expenses
                        WHERE strftime('%Y', date) = ? 
                        AND strftime('%m', date) = ?
                        GROUP BY month
                        """,
                        (f"{year:04d}", f"{month:02d}")
                    )
                else:
                    # All months in the year
                    cursor.execute(
                        """
                        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
                        FROM expenses
                        WHERE strftime('%Y', date) = ?
                        GROUP BY month
                        ORDER BY month
                        """,
                        (f"{year:04d}",)
                    )
                
                rows = cursor.fetchall()
                totals = {row['month']: row['total'] for row in rows}
                
                logger.debug(f"Calculated totals for {len(totals)} months")
                return totals
        except ValueError as e:
            logger.error(f"Invalid parameter: {str(e)}")
            raise
        except sqlite3.Error as e:
            logger.error(f"Failed to calculate monthly totals: {str(e)}")
            raise
    
    def group_expenses_by_category(self) -> Dict[str, Dict[str, Any]]:
        """
        Group and analyze expenses by category.
        
        Returns:
            Dict with category data including:
            - count: Number of expenses in category
            - total: Total spending in category
            - average: Average expense amount in category
            - percentage: Percentage of total spending
            - expenses: List of individual expenses
        
        Raises:
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> grouped = db.group_expenses_by_category()
            >>> for category, data in grouped.items():
            ...     print(f"{category}: ${data['total']:.2f} "
            ...           f"({data['count']} items, "
            ...           f"{data['percentage']:.1f}%)")
        """
        try:
            with self._get_cursor() as cursor:
                # Get category totals
                cursor.execute(
                    """
                    SELECT category, COUNT(*) as count, SUM(amount) as total, 
                           AVG(amount) as average
                    FROM expenses
                    GROUP BY category
                    ORDER BY total DESC
                    """
                )
                rows = cursor.fetchall()
                
                # Calculate grand total for percentages
                cursor.execute("SELECT SUM(amount) as grand_total FROM expenses")
                grand_total_row = cursor.fetchone()
                grand_total = grand_total_row['grand_total'] or 0
                
                # Build result dictionary
                grouped = {}
                for row in rows:
                    category = row['category']
                    total = row['total']
                    percentage = (total / grand_total * 100) if grand_total > 0 else 0
                    
                    # Get expenses for this category
                    cursor.execute(
                        """
                        SELECT id, date, merchant, amount, notes
                        FROM expenses
                        WHERE category = ?
                        ORDER BY date DESC
                        """,
                        (category,)
                    )
                    expenses = [dict(exp) for exp in cursor.fetchall()]
                    
                    grouped[category] = {
                        'count': row['count'],
                        'total': total,
                        'average': row['average'],
                        'percentage': percentage,
                        'expenses': expenses
                    }
                
                logger.debug(f"Grouped expenses into {len(grouped)} categories")
                return grouped
        except sqlite3.Error as e:
            logger.error(f"Failed to group expenses by category: {str(e)}")
            raise
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for all expenses.
        
        Returns:
            Dict with:
            - total_expenses: Total number of expenses
            - total_spending: Total amount spent
            - average_expense: Average expense amount
            - max_expense: Highest single expense
            - min_expense: Lowest single expense
            - categories_count: Number of different categories
            - date_range: Date range of expenses
        
        Raises:
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> stats = db.get_summary_statistics()
            >>> print(f"Total spending: ${stats['total_spending']:.2f}")
            >>> print(f"Average expense: ${stats['average_expense']:.2f}")
            >>> print(f"Highest expense: ${stats['max_expense']:.2f}")
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        COUNT(*) as total_expenses,
                        SUM(amount) as total_spending,
                        AVG(amount) as average_expense,
                        MAX(amount) as max_expense,
                        MIN(amount) as min_expense,
                        COUNT(DISTINCT category) as categories_count,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date
                    FROM expenses
                    """
                )
                row = cursor.fetchone()
                
                stats = {
                    'total_expenses': row['total_expenses'] or 0,
                    'total_spending': row['total_spending'] or 0,
                    'average_expense': row['average_expense'] or 0,
                    'max_expense': row['max_expense'] or 0,
                    'min_expense': row['min_expense'] or 0,
                    'categories_count': row['categories_count'] or 0,
                    'date_range': {
                        'start': row['earliest_date'],
                        'end': row['latest_date']
                    }
                }
                
                logger.debug("Calculated summary statistics")
                return stats
        except sqlite3.Error as e:
            logger.error(f"Failed to get summary statistics: {str(e)}")
            raise
    
    def update_expense(self, expense_id: int, **kwargs) -> bool:
        """
        Update an existing expense record.
        
        Args:
            expense_id: ID of expense to update
            **kwargs: Fields to update (date, merchant, category, amount, notes)
        
        Returns:
            bool: True if update was successful
        
        Raises:
            ValueError: If expense ID not found or invalid data
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> success = db.update_expense(1, amount=7.50, notes="Updated")
            >>> if success:
            ...     print("Expense updated successfully")
        """
        try:
            # Verify expense exists
            if not self.fetch_expense_by_id(expense_id):
                raise ValueError(f"Expense with ID {expense_id} not found")
            
            # Build update query
            allowed_fields = {'date', 'merchant', 'category', 'amount', 'notes'}
            update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not update_fields:
                logger.warning("No valid fields provided for update")
                return False
            
            set_clause = ", ".join([f"{field} = ?" for field in update_fields])
            set_clause += ", updated_at = CURRENT_TIMESTAMP"
            values = list(update_fields.values()) + [expense_id]
            
            with self._get_cursor() as cursor:
                cursor.execute(
                    f"UPDATE expenses SET {set_clause} WHERE id = ?",
                    values
                )
                
                logger.info(f"Updated expense ID {expense_id}: {update_fields}")
                return cursor.rowcount > 0
        except (ValueError, sqlite3.Error) as e:
            logger.error(f"Failed to update expense: {str(e)}")
            raise
    
    def delete_expense(self, expense_id: int) -> bool:
        """
        Delete an expense record from the database.
        
        Args:
            expense_id: ID of expense to delete
        
        Returns:
            bool: True if deletion was successful
        
        Raises:
            ValueError: If expense ID not found
            sqlite3.Error: If database operation fails
        
        Example:
            >>> db = DatabaseManager()
            >>> success = db.delete_expense(1)
            >>> if success:
            ...     print("Expense deleted successfully")
        """
        try:
            # Verify expense exists
            if not self.fetch_expense_by_id(expense_id):
                raise ValueError(f"Expense with ID {expense_id} not found")
            
            with self._get_cursor() as cursor:
                cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                
                logger.info(f"Deleted expense ID {expense_id}")
                return cursor.rowcount > 0
        except (ValueError, sqlite3.Error) as e:
            logger.error(f"Failed to delete expense: {str(e)}")
            raise
    
    def delete_all_expenses(self) -> int:
        """
        Delete all expense records from the database.
        
        Returns:
            int: Number of expenses deleted
        
        Raises:
            sqlite3.Error: If database operation fails
        
        Warning:
            This operation cannot be undone. Use with caution.
        
        Example:
            >>> db = DatabaseManager()
            >>> count = db.delete_all_expenses()
            >>> print(f"Deleted {count} expenses")
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute("DELETE FROM expenses")
                count = cursor.rowcount
                
                logger.warning(f"Deleted all {count} expenses from database")
                return count
        except sqlite3.Error as e:
            logger.error(f"Failed to delete all expenses: {str(e)}")
            raise
    
    def close(self) -> None:
        """
        Close the database connection.
        
        Example:
            >>> db = DatabaseManager()
            >>> # ... perform operations ...
            >>> db.close()
        """
        if self.connection:
            try:
                self.connection.close()
                logger.info("Database connection closed")
            except sqlite3.Error as e:
                logger.error(f"Error closing database: {str(e)}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_connection(db_path: str = "finsight_expenses.db") -> sqlite3.Connection:
    """
    Create a connection to the SQLite database.
    
    Args:
        db_path: Path to database file
    
    Returns:
        sqlite3.Connection: Database connection
    
    Raises:
        sqlite3.Error: If connection fails
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        logger.info(f"Database connection created: {db_path}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to create database connection: {str(e)}")
        raise


def close_connection(conn: sqlite3.Connection) -> None:
    """
    Close a database connection.
    
    Args:
        conn: sqlite3.Connection to close
    """
    try:
        if conn:
            conn.close()
            logger.info("Database connection closed")
    except sqlite3.Error as e:
        logger.error(f"Error closing connection: {str(e)}")
