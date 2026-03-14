# Database Module - Quick Reference Guide

## 🚀 Quick Start

```python
from src.database import DatabaseManager, ExpenseRecord

# Create database connection
with DatabaseManager() as db:
    # Create expense
    expense = ExpenseRecord(
        date="2024-03-13",
        merchant="Starbucks",
        category="food & dining",
        amount=6.50
    )
    
    # Insert
    expense_id = db.insert_expense(expense)
    
    # Fetch
    all_expenses = db.fetch_all_expenses()
    
    # Analyze
    grouped = db.group_expenses_by_category()
    stats = db.get_summary_statistics()
```

---

## 📋 Common Tasks

### Insert Expenses

```python
# Single expense
expense = ExpenseRecord(
    date="2024-03-13",
    merchant="Store",
    category="shopping",
    amount=99.99
)
expense_id = db.insert_expense(expense)

# Multiple expenses
expenses = [
    ExpenseRecord(...),
    ExpenseRecord(...),
]
ids = db.insert_expenses_batch(expenses)
```

### Fetch Expenses

```python
# All expenses
all_expenses = db.fetch_all_expenses()

# By ID
expense = db.fetch_expense_by_id(5)

# By date range
expenses = db.fetch_expenses_by_date_range("2024-03-01", "2024-03-31")

# By category
food = db.fetch_expenses_by_category("food & dining")
```

### Analyze Data

```python
# Category breakdown
grouped = db.group_expenses_by_category()
for cat, data in grouped.items():
    print(f"{cat}: ${data['total']:.2f} ({data['percentage']:.1f}%)")

# Monthly totals
monthly = db.calculate_monthly_totals(year=2024)
for month, total in monthly.items():
    print(f"{month}: ${total:.2f}")

# Overall statistics
stats = db.get_summary_statistics()
print(f"Total: ${stats['total_spending']:.2f}")
print(f"Average: ${stats['average_expense']:.2f}")
```

### Update/Delete

```python
# Update expense
db.update_expense(expense_id, amount=10.00, notes="Updated")

# Delete expense
db.delete_expense(expense_id)

# Delete all
db.delete_all_expenses()
```

---

## 📊 ExpenseRecord Fields

```python
ExpenseRecord(
    date="YYYY-MM-DD",          # Required
    merchant="Store Name",       # Required
    category="Category Name",    # Required
    amount=99.99,                # Required, must be > 0
    notes="Optional notes",      # Optional, default ""
    id=None,                     # Auto-assigned (read-only)
    created_at=None              # Auto-assigned (read-only)
)
```

---

## 🎯 Category Grouping Format

```python
grouped = db.group_expenses_by_category()
# Returns:
{
    "category_name": {
        "count": 5,
        "total": 250.50,
        "average": 50.10,
        "percentage": 25.5,
        "expenses": [
            {"id": 1, "date": "2024-03-13", "merchant": "Store", "amount": 50.00},
            ...
        ]
    },
    ...
}
```

---

## 📈 Summary Statistics Format

```python
stats = db.get_summary_statistics()
# Returns:
{
    "total_expenses": 42,
    "total_spending": 2500.50,
    "average_expense": 59.54,
    "max_expense": 500.00,
    "min_expense": 5.50,
    "categories_count": 8,
    "date_range": {
        "start": "2024-03-01",
        "end": "2024-03-31"
    }
}
```

---

## 🔧 Context Manager (Recommended)

```python
# Automatically closes connection
with DatabaseManager() as db:
    expenses = db.fetch_all_expenses()
    # Connection closed automatically here
```

---

## ❌ Validation Rules

| Field | Rule | Example |
|-------|------|---------|
| `date` | YYYY-MM-DD format | "2024-03-13" |
| `merchant` | Cannot be empty | "Starbucks" |
| `category` | Cannot be empty | "food & dining" |
| `amount` | Must be > 0 | 6.50 |

---

## 🧪 Running Tests

```bash
# All tests
python -m pytest src/database/test_db_manager.py -v

# Specific test class
python -m pytest src/database/test_db_manager.py::TestExpenseInsertion -v

# With coverage
python -m pytest src/database/test_db_manager.py --cov=src.database
```

---

## 📚 API Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `insert_expense()` | Insert single | expense_id |
| `insert_expenses_batch()` | Insert multiple | [ids] |
| `fetch_all_expenses()` | Get all | [ExpenseRecord] |
| `fetch_expense_by_id()` | Get by ID | ExpenseRecord or None |
| `fetch_expenses_by_date_range()` | Get by date range | [ExpenseRecord] |
| `fetch_expenses_by_category()` | Get by category | [ExpenseRecord] |
| `calculate_monthly_totals()` | Monthly totals | {month: total} |
| `group_expenses_by_category()` | Category stats | {category: stats} |
| `get_summary_statistics()` | Overall stats | stats_dict |
| `update_expense()` | Update record | bool |
| `delete_expense()` | Delete record | bool |
| `delete_all_expenses()` | Delete all | count |
| `close()` | Close connection | None |

---

## 💾 Database Location

- Default: `finsight_expenses.db` (current directory)
- Custom: `DatabaseManager("path/to/database.db")`

---

## 🐛 Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: merchant cannot be empty` | Missing merchant | Provide merchant name |
| `ValueError: amount must be > 0` | Invalid amount | Use positive number |
| `ValueError: Invalid date format` | Wrong date format | Use YYYY-MM-DD |
| `sqlite3.OperationalError: no such table` | Table not created | Reinitialize db |

---

## 📝 Examples

See `src/database/db_examples.py` for 12 detailed examples:

1. Basic setup
2. Single expense insertion
3. Batch insertion
4. Fetching all expenses
5. Date range fetching
6. Category fetching
7. Monthly totals
8. Category analysis
9. Summary statistics
10. Updating expenses
11. Deleting expenses
12. Budget analysis

---

## 🔗 Full Documentation

See `DATABASE_MODULE.md` for comprehensive documentation including:
- Architecture details
- Complete API reference
- Advanced usage patterns
- Performance tuning
- Security considerations
- Troubleshooting guide

---

## ✅ Production Ready

- ✓ 100% type hints
- ✓ Full docstrings
- ✓ Error handling
- ✓ 33+ unit tests
- ✓ SQL injection prevention
- ✓ Transaction support
- ✓ Logging

---

**Status:** Ready to use! 🚀
