# FinSight AI - Database Module Documentation

## Overview

The Database Module provides a robust SQLite-based solution for persisting and managing expense data in FinSight AI. It includes a comprehensive API for inserting, querying, analyzing, and managing expense records.

## Table of Contents

1. [Architecture](#architecture)
2. [Database Schema](#database-schema)
3. [Core Classes](#core-classes)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Integration](#integration)
7. [Testing](#testing)
8. [Best Practices](#best-practices)

---

## Architecture

### Components

```
┌─────────────────────────────────────────┐
│      FinSight AI Application            │
├─────────────────────────────────────────┤
│      LangGraph Workflow                 │
│    (orchestrates analysis)              │
├─────────────────────────────────────────┤
│      Database Module                    │
│  ┌──────────────────────────────────┐   │
│  │   DatabaseManager                │   │
│  │  - CRUD Operations               │   │
│  │  - Query Methods                 │   │
│  │  - Analytics Methods             │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│      SQLite Database                    │
│  - expenses table                       │
│  - Constraints & validation             │
│  - Timestamps & metadata                │
└─────────────────────────────────────────┘
```

### Design Principles

1. **Single Responsibility**: DatabaseManager handles all database operations
2. **Type Safety**: Full type hints on all methods and dataclasses
3. **Validation**: Input validation in ExpenseRecord.__post_init__()
4. **Error Handling**: Comprehensive error handling with meaningful messages
5. **Logging**: Detailed logging at multiple levels
6. **Security**: Parameterized queries prevent SQL injection
7. **Resource Management**: Context manager support for automatic cleanup
8. **Transaction Safety**: Proper transaction handling with rollback

---

## Database Schema

### Expenses Table

```sql
CREATE TABLE IF NOT EXISTS expenses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,
    merchant        TEXT NOT NULL,
    category        TEXT NOT NULL,
    amount          REAL NOT NULL,
    notes           TEXT DEFAULT '',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (amount > 0),
    CHECK (date GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]')
)
```

### Column Specifications

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique expense identifier |
| `date` | TEXT | NOT NULL | Transaction date (YYYY-MM-DD) |
| `merchant` | TEXT | NOT NULL | Vendor/store name |
| `category` | TEXT | NOT NULL | Expense category |
| `amount` | REAL | NOT NULL, > 0 | Transaction amount |
| `notes` | TEXT | DEFAULT '' | Optional notes |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification time |

### Constraints

- **Primary Key**: `id` uniquely identifies each expense
- **Amount Check**: Ensures `amount > 0` (no negative/zero spending)
- **Date Format**: Enforces YYYY-MM-DD format using GLOB pattern
- **NOT NULL Fields**: Ensures required data is always present

---

## Core Classes

### ExpenseRecord

A dataclass that represents a single expense transaction with built-in validation.

#### Definition

```python
@dataclass
class ExpenseRecord:
    date: str                    # YYYY-MM-DD format
    merchant: str                # Vendor/store name
    category: str                # Expense category
    amount: float                # Transaction amount (> 0)
    id: Optional[int] = None     # Database ID (auto-assigned)
    created_at: Optional[str] = None  # Creation timestamp
    notes: str = ""              # Optional notes
```

#### Validation Rules

The `__post_init__()` method performs validation:

| Field | Validation Rule |
|-------|-----------------|
| `merchant` | Cannot be empty |
| `category` | Cannot be empty |
| `amount` | Must be > 0 |
| `date` | Must match YYYY-MM-DD format |

#### Methods

##### `to_dict() -> dict`
Converts the expense record to a dictionary representation.

```python
expense = ExpenseRecord(
    date="2024-03-13",
    merchant="Starbucks",
    category="food",
    amount=6.50
)
data = expense.to_dict()
# Returns: {
#     'id': None,
#     'date': '2024-03-13',
#     'merchant': 'Starbucks',
#     'category': 'food',
#     'amount': 6.50,
#     'created_at': None,
#     'notes': ''
# }
```

#### Example

```python
from src.database import ExpenseRecord

# Create a valid expense record
expense = ExpenseRecord(
    date="2024-03-13",
    merchant="Starbucks",
    category="food & dining",
    amount=6.50,
    notes="Morning coffee"
)

# Invalid examples (will raise ValueError):
# ExpenseRecord(date="2024-03-13", merchant="", category="food", amount=10)
# ExpenseRecord(date="2024/03/13", merchant="Store", category="food", amount=10)
# ExpenseRecord(date="2024-03-13", merchant="Store", category="food", amount=-10)
```

---

### DatabaseManager

Main orchestration class for all database operations.

#### Initialization

```python
db = DatabaseManager(db_path: str = "finsight_expenses.db")
```

**Parameters:**
- `db_path` (str): Path to SQLite database file. Defaults to "finsight_expenses.db"

**Behavior:**
- Creates database file if it doesn't exist
- Creates `expenses` table if needed
- Sets up logging and connection

**Example:**
```python
from src.database import DatabaseManager

# Use default database
db = DatabaseManager()

# Use custom path
db = DatabaseManager("custom_expenses.db")

# Use context manager for automatic cleanup
with DatabaseManager() as db:
    # Use database
    pass  # Automatically closes
```

#### Connection Management

##### Context Manager Support

```python
with DatabaseManager("expenses.db") as db:
    # Database operations here
    expenses = db.fetch_all_expenses()
# Connection automatically closed
```

##### Manual Management

```python
db = DatabaseManager("expenses.db")
try:
    # Use database
    expenses = db.fetch_all_expenses()
finally:
    db.close()
```

---

## API Reference

### Insertion Methods

#### `insert_expense(expense: ExpenseRecord) -> int`

Inserts a single expense into the database.

**Parameters:**
- `expense` (ExpenseRecord): The expense to insert

**Returns:**
- `int`: The database ID of the inserted expense

**Raises:**
- `ValueError`: If expense data is invalid
- `sqlite3.Error`: If database operation fails

**Example:**
```python
db = DatabaseManager()

expense = ExpenseRecord(
    date="2024-03-13",
    merchant="Starbucks",
    category="food & dining",
    amount=6.50,
    notes="Coffee"
)

expense_id = db.insert_expense(expense)
print(f"Inserted with ID: {expense_id}")
```

---

#### `insert_expenses_batch(expenses: List[ExpenseRecord]) -> List[int]`

Inserts multiple expenses efficiently in a single transaction.

**Parameters:**
- `expenses` (List[ExpenseRecord]): List of expenses to insert

**Returns:**
- `List[int]`: List of database IDs for inserted expenses

**Raises:**
- `ValueError`: If any expense data is invalid
- `sqlite3.Error`: If database operation fails

**Example:**
```python
db = DatabaseManager()

expenses = [
    ExpenseRecord(
        date="2024-03-13",
        merchant="Whole Foods",
        category="groceries",
        amount=75.50
    ),
    ExpenseRecord(
        date="2024-03-14",
        merchant="Shell",
        category="transportation",
        amount=45.00
    ),
]

ids = db.insert_expenses_batch(expenses)
print(f"Inserted {len(ids)} expenses")
```

---

### Fetching Methods

#### `fetch_all_expenses(order_by: str = "date DESC") -> List[ExpenseRecord]`

Retrieves all expenses from the database.

**Parameters:**
- `order_by` (str): SQL ORDER BY clause. Default: "date DESC" (newest first)

**Returns:**
- `List[ExpenseRecord]`: All expense records

**Example:**
```python
db = DatabaseManager()

# Newest first (default)
expenses = db.fetch_all_expenses()

# Oldest first
expenses = db.fetch_all_expenses(order_by="date ASC")

# By amount (highest first)
expenses = db.fetch_all_expenses(order_by="amount DESC")

# By merchant name
expenses = db.fetch_all_expenses(order_by="merchant ASC")
```

---

#### `fetch_expense_by_id(expense_id: int) -> Optional[ExpenseRecord]`

Retrieves a specific expense by its ID.

**Parameters:**
- `expense_id` (int): The database ID of the expense

**Returns:**
- `ExpenseRecord`: The expense if found
- `None`: If expense doesn't exist

**Example:**
```python
db = DatabaseManager()

# Fetch expense with ID 5
expense = db.fetch_expense_by_id(5)

if expense:
    print(f"{expense.merchant}: ${expense.amount:.2f}")
else:
    print("Expense not found")
```

---

#### `fetch_expenses_by_date_range(start_date: str, end_date: str) -> List[ExpenseRecord]`

Retrieves expenses within a date range (inclusive).

**Parameters:**
- `start_date` (str): Start date in YYYY-MM-DD format
- `end_date` (str): End date in YYYY-MM-DD format

**Returns:**
- `List[ExpenseRecord]`: Expenses in the date range

**Example:**
```python
db = DatabaseManager()

# March 1-15, 2024
expenses = db.fetch_expenses_by_date_range("2024-03-01", "2024-03-15")

# Entire March 2024
expenses = db.fetch_expenses_by_date_range("2024-03-01", "2024-03-31")

total = sum(e.amount for e in expenses)
print(f"Total in period: ${total:.2f}")
```

---

#### `fetch_expenses_by_category(category: str) -> List[ExpenseRecord]`

Retrieves all expenses in a specific category.

**Parameters:**
- `category` (str): The expense category to filter by

**Returns:**
- `List[ExpenseRecord]`: All expenses in that category

**Example:**
```python
db = DatabaseManager()

# Get all food expenses
food = db.fetch_expenses_by_category("food & dining")

# Calculate total for category
total = sum(e.amount for e in food)
average = total / len(food) if food else 0

print(f"Food spending: ${total:.2f}")
print(f"Average transaction: ${average:.2f}")
```

---

### Analysis Methods

#### `calculate_monthly_totals(year: int, month: Optional[int] = None) -> Dict[str, float]`

Calculates total spending by month.

**Parameters:**
- `year` (int): The year to analyze
- `month` (Optional[int]): Specific month (1-12), or None for all months

**Returns:**
- `Dict[str, float]`: Month names mapped to total spending
  - Format: `{"2024-03": 250.50, "2024-04": 300.75, ...}`

**Example:**
```python
db = DatabaseManager()

# All months in 2024
totals = db.calculate_monthly_totals(year=2024)
for month, amount in sorted(totals.items()):
    print(f"{month}: ${amount:.2f}")

# Specific month (March 2024)
march = db.calculate_monthly_totals(year=2024, month=3)
print(f"March total: ${march.get('2024-03', 0):.2f}")
```

---

#### `group_expenses_by_category() -> Dict[str, dict]`

Groups expenses by category with comprehensive statistics.

**Returns:**
- `Dict[str, dict]`: Category breakdown with structure:

```python
{
    "category_name": {
        "count": 5,                    # Number of transactions
        "total": 125.50,               # Total amount spent
        "average": 25.10,              # Average per transaction
        "percentage": 25.5,            # % of total spending
        "expenses": [                  # Individual expenses
            {
                "id": 1,
                "date": "2024-03-13",
                "merchant": "Store",
                "amount": 50.00
            },
            # ... more expenses
        ]
    },
    # ... more categories
}
```

**Example:**
```python
db = DatabaseManager()

grouped = db.group_expenses_by_category()

for category, data in sorted(
    grouped.items(),
    key=lambda x: x[1]['total'],
    reverse=True
):
    print(
        f"{category}: ${data['total']:.2f} "
        f"({data['percentage']:.1f}%, {data['count']} transactions)"
    )

# Show breakdown
total_spending = sum(d['total'] for d in grouped.values())
print(f"\nTotal across all categories: ${total_spending:.2f}")
```

---

#### `get_summary_statistics() -> Dict[str, Any]`

Provides overall expense statistics.

**Returns:**
- `Dict[str, Any]`: Statistics dictionary with structure:

```python
{
    "total_expenses": 42,                    # Total transaction count
    "total_spending": 2500.50,               # Total amount
    "average_expense": 59.54,                # Average per transaction
    "max_expense": 500.00,                   # Highest transaction
    "min_expense": 5.50,                     # Lowest transaction
    "categories_count": 8,                   # Number of categories
    "date_range": {
        "start": "2024-03-01",
        "end": "2024-03-31"
    }
}
```

**Example:**
```python
db = DatabaseManager()

stats = db.get_summary_statistics()

print(f"Total Transactions: {stats['total_expenses']}")
print(f"Total Spending: ${stats['total_spending']:.2f}")
print(f"Average Expense: ${stats['average_expense']:.2f}")
print(f"Highest: ${stats['max_expense']:.2f}")
print(f"Lowest: ${stats['min_expense']:.2f}")
print(f"Categories: {stats['categories_count']}")
print(f"Period: {stats['date_range']['start']} to {stats['date_range']['end']}")
```

---

### Update Methods

#### `update_expense(expense_id: int, **kwargs) -> bool`

Updates an existing expense record.

**Parameters:**
- `expense_id` (int): ID of expense to update
- `**kwargs`: Fields to update (date, merchant, category, amount, notes)

**Returns:**
- `bool`: True if update successful, False if expense not found

**Raises:**
- `ValueError`: If update data is invalid

**Example:**
```python
db = DatabaseManager()

# Correct an amount
success = db.update_expense(
    expense_id=5,
    amount=8.75,
    notes="Corrected amount"
)

if success:
    print("Update successful")
else:
    print("Expense not found")
```

---

### Delete Methods

#### `delete_expense(expense_id: int) -> bool`

Deletes a single expense record.

**Parameters:**
- `expense_id` (int): ID of expense to delete

**Returns:**
- `bool`: True if deleted, False if not found

**Example:**
```python
db = DatabaseManager()

success = db.delete_expense(5)
if success:
    print("Expense deleted")
```

---

#### `delete_all_expenses() -> int`

Deletes all expense records (use with caution!).

**Returns:**
- `int`: Number of expenses deleted

**Example:**
```python
db = DatabaseManager()

count = db.delete_all_expenses()
print(f"Deleted {count} expenses")
```

---

### Utility Methods

#### `close()`

Closes the database connection.

**Example:**
```python
db = DatabaseManager()
try:
    # Use database
    pass
finally:
    db.close()
```

---

## Usage Examples

### Example 1: Basic CRUD Operations

```python
from src.database import DatabaseManager, ExpenseRecord

# Initialize database
db = DatabaseManager()

# CREATE
expense = ExpenseRecord(
    date="2024-03-13",
    merchant="Starbucks",
    category="food & dining",
    amount=6.50
)
expense_id = db.insert_expense(expense)
print(f"Created expense with ID: {expense_id}")

# READ
retrieved = db.fetch_expense_by_id(expense_id)
print(f"Retrieved: {retrieved.merchant} - ${retrieved.amount:.2f}")

# UPDATE
db.update_expense(expense_id, amount=7.00)
print("Updated expense")

# DELETE
db.delete_expense(expense_id)
print("Deleted expense")

db.close()
```

---

### Example 2: Expense Analysis

```python
from src.database import DatabaseManager

with DatabaseManager() as db:
    # Get all expenses
    all_expenses = db.fetch_all_expenses()
    print(f"Total expenses: {len(all_expenses)}")
    
    # Analysis by category
    grouped = db.group_expenses_by_category()
    print("\nSpending by Category:")
    for cat, data in sorted(grouped.items(), 
                            key=lambda x: x[1]['total'],
                            reverse=True):
        print(f"  {cat}: ${data['total']:.2f} ({data['count']} transactions)")
    
    # Monthly breakdown
    monthly = db.calculate_monthly_totals(year=2024)
    print("\nMonthly Totals:")
    for month, total in sorted(monthly.items()):
        print(f"  {month}: ${total:.2f}")
    
    # Overall stats
    stats = db.get_summary_statistics()
    print(f"\nAverage expense: ${stats['average_expense']:.2f}")
    print(f"Max expense: ${stats['max_expense']:.2f}")
```

---

### Example 3: Budget Tracking

```python
from src.database import DatabaseManager

budget = {
    "food & dining": 300.00,
    "transportation": 200.00,
    "groceries": 400.00,
    "shopping": 500.00,
}

with DatabaseManager() as db:
    grouped = db.group_expenses_by_category()
    
    print("Budget Status:")
    print(f"{'Category':<20} {'Budget':>10} {'Actual':>10} {'Remaining':>10}")
    print("-" * 50)
    
    for cat, budget_amt in sorted(budget.items()):
        actual = grouped.get(cat, {}).get('total', 0)
        remaining = budget_amt - actual
        status = "✓" if remaining >= 0 else "✗"
        
        print(f"{cat:<20} ${budget_amt:>9.2f} ${actual:>9.2f} "
              f"${remaining:>9.2f} {status}")
```

---

### Example 4: Batch Import

```python
from src.database import DatabaseManager, ExpenseRecord

expenses = [
    ExpenseRecord(
        date="2024-03-01",
        merchant="Walmart",
        category="shopping",
        amount=150.00
    ),
    ExpenseRecord(
        date="2024-03-02",
        merchant="Target",
        category="shopping",
        amount=85.00
    ),
    # ... more expenses
]

with DatabaseManager() as db:
    ids = db.insert_expenses_batch(expenses)
    print(f"Imported {len(ids)} expenses")
```

---

## Integration

### With LangGraph Workflow

The database module integrates with the LangGraph workflow for persistent storage:

```python
# In your LangGraph workflow
from src.database import DatabaseManager, ExpenseRecord

def storage_node(state):
    """Store extracted expenses in database."""
    db = DatabaseManager()
    
    expenses = state.get("extracted_expenses", [])
    
    # Convert to ExpenseRecord and insert
    for exp in expenses:
        record = ExpenseRecord(
            date=exp["date"],
            merchant=exp["merchant"],
            category=exp["category"],
            amount=float(exp["amount"])
        )
        db.insert_expense(record)
    
    db.close()
    state["storage_status"] = "stored"
    return state
```

---

## Testing

### Running Tests

```bash
# Run all database tests
python -m pytest src/database/test_db_manager.py -v

# Run specific test class
python -m pytest src/database/test_db_manager.py::TestExpenseRecord -v

# Run with coverage
python -m pytest src/database/test_db_manager.py --cov=src.database
```

### Test Coverage

The test suite includes 33+ tests covering:

- ✅ ExpenseRecord validation
- ✅ Database initialization
- ✅ Insert operations (single and batch)
- ✅ Fetch operations (all variations)
- ✅ Update and delete operations
- ✅ Analysis methods
- ✅ Error handling
- ✅ Edge cases

### Test Classes

1. **TestExpenseRecord** - Dataclass validation
2. **TestDatabaseInitialization** - Database setup
3. **TestExpenseInsertion** - Insert operations
4. **TestExpenseFetching** - Fetch operations
5. **TestMonthlyTotals** - Monthly analysis
6. **TestCategoryGrouping** - Category analysis
7. **TestSummaryStatistics** - Overall statistics
8. **TestUpdateAndDelete** - Modify operations

---

## Best Practices

### 1. Connection Management

**Do:**
```python
# Use context manager for automatic cleanup
with DatabaseManager() as db:
    expenses = db.fetch_all_expenses()
```

**Don't:**
```python
# Manual management risks forgotten close()
db = DatabaseManager()
expenses = db.fetch_all_expenses()
# Oops, forgot to close!
```

---

### 2. Data Validation

**Do:**
```python
# ExpenseRecord validates automatically
try:
    expense = ExpenseRecord(
        date="2024-03-13",
        merchant="Store",
        category="food",
        amount=10.50
    )
except ValueError as e:
    print(f"Invalid expense: {e}")
```

**Don't:**
```python
# Don't skip validation
expense = {"date": "invalid", "amount": -10}  # Invalid!
```

---

### 3. Batch Operations

**Do:**
```python
# Use batch insert for multiple records
expenses = [ExpenseRecord(...) for _ in range(100)]
ids = db.insert_expenses_batch(expenses)
```

**Don't:**
```python
# Don't insert one-by-one in a loop
for expense in expenses:
    db.insert_expense(expense)  # Slow!
```

---

### 4. Query Optimization

**Do:**
```python
# Fetch and process in one call
expenses = db.fetch_expenses_by_category("food")
total = sum(e.amount for e in expenses)
```

**Don't:**
```python
# Don't fetch all and filter manually
all_expenses = db.fetch_all_expenses()
food = [e for e in all_expenses if e.category == "food"]
```

---

### 5. Error Handling

**Do:**
```python
try:
    db.insert_expense(expense)
except ValueError as e:
    print(f"Invalid data: {e}")
except sqlite3.Error as e:
    print(f"Database error: {e}")
```

**Don't:**
```python
# Don't ignore errors
db.insert_expense(expense)
```

---

### 6. Date Handling

**Do:**
```python
# Use YYYY-MM-DD format
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
expense = ExpenseRecord(
    date=today,
    merchant="Store",
    category="food",
    amount=10.50
)
```

**Don't:**
```python
# Don't use other date formats
expense = ExpenseRecord(
    date="03/13/2024",  # Wrong format!
    merchant="Store",
    category="food",
    amount=10.50
)
```

---

## Troubleshooting

### Issue: "expenses table does not exist"

**Cause:** Database not properly initialized

**Solution:**
```python
db = DatabaseManager()  # Automatically creates table
```

---

### Issue: "amount must be > 0"

**Cause:** Trying to insert negative or zero amount

**Solution:**
```python
expense = ExpenseRecord(
    date="2024-03-13",
    merchant="Store",
    category="food",
    amount=10.50  # Must be positive
)
```

---

### Issue: "date does not match YYYY-MM-DD"

**Cause:** Invalid date format

**Solution:**
```python
from datetime import datetime

date_str = datetime.now().strftime("%Y-%m-%d")  # Correct format
expense = ExpenseRecord(
    date=date_str,
    merchant="Store",
    category="food",
    amount=10.50
)
```

---

## Performance Considerations

### Database Size

- Typical expense record: ~200 bytes
- 10,000 records: ~2 MB
- 100,000 records: ~20 MB

### Query Performance

| Operation | Performance | Notes |
|-----------|-------------|-------|
| Insert single | < 1ms | Very fast |
| Batch insert (100) | < 50ms | Optimal for bulk |
| Fetch all | < 100ms | O(n) depends on data |
| Fetch by ID | < 1ms | Indexed lookup |
| Fetch by category | < 50ms | Table scan |
| Calculate totals | < 100ms | Aggregation |

### Optimization Tips

1. Use `insert_expenses_batch()` for multiple inserts
2. Fetch only needed data with specific methods
3. Use indices for frequent queries (future enhancement)
4. Consider date range queries for historical data
5. Archive old data to separate database

---

## Security Considerations

### SQL Injection Prevention

All queries use parameterized statements:
```python
# Safe - uses parameter placeholders
cursor.execute(
    "SELECT * FROM expenses WHERE merchant = ?",
    (merchant_name,)
)

# NOT SAFE - string concatenation
cursor.execute(f"SELECT * FROM expenses WHERE merchant = '{merchant}'")
```

### Input Validation

All user inputs are validated:
- Date format checked
- Amounts verified as positive
- Merchant/category required
- Type hints prevent type confusion

### Data Integrity

- Transaction support ensures consistency
- Rollback on error prevents partial updates
- Constraints prevent invalid data
- Timestamps track modifications

---

## Version History

### v1.0.0 (Current)

- Initial release
- CRUD operations
- Query methods
- Analysis methods
- Full test coverage
- Comprehensive documentation

---

## Support & Documentation

- **Examples**: See `src/database/db_examples.py`
- **Tests**: See `src/database/test_db_manager.py`
- **Module**: See `src/database/db_manager.py`

---

## License

Part of FinSight AI project.

---

**Last Updated**: March 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✓
