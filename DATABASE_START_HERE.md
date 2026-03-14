# 🚀 FinSight AI Database Module - START HERE

Welcome! This guide will help you understand and use the FinSight AI Database Module.

---

## ⚡ 30-Second Overview

The **Database Module** provides a complete SQLite-based solution for managing expense data in FinSight AI.

### What It Does

```python
from src.database import DatabaseManager, ExpenseRecord

# Create database
db = DatabaseManager()

# Insert expenses
expense = ExpenseRecord(date="2024-03-13", merchant="Starbucks", 
                       category="food", amount=6.50)
db.insert_expense(expense)

# Analyze spending
grouped = db.group_expenses_by_category()
stats = db.get_summary_statistics()

# Clean up
db.close()
```

### Key Features

✅ Store expenses in SQLite database  
✅ Query by date, category, amount  
✅ Calculate monthly totals  
✅ Analyze spending patterns  
✅ Update and delete records  
✅ Production-ready quality  

---

## 📚 Documentation Guide

### For Different Reading Levels

**⏱️ 5 Minutes - Quick Start**
→ Read: `DATABASE_QUICK_REFERENCE.md`
- Common tasks
- Quick API reference
- Common errors

**⏱️ 15 Minutes - Overview**
→ Read: This file + code examples
- Architecture overview
- Basic usage
- Key concepts

**⏱️ 30 Minutes - Complete Understanding**
→ Read: `DATABASE_DELIVERY_SUMMARY.md`
- Full requirements
- File organization
- Integration guide

**⏱️ 60 Minutes - Deep Dive**
→ Read: `DATABASE_MODULE.md`
- Complete API reference
- All examples
- Best practices
- Troubleshooting

**⏱️ Hands-On Learning**
→ Run: `src/database/db_examples.py`
- 12 working examples
- Copy and adapt
- Experiment

---

## 🎯 Choose Your Path

### Path 1: "Just Show Me How to Use It" 👈 START HERE

**Step 1:** Read DATABASE_QUICK_REFERENCE.md (5 min)

**Step 2:** Copy this code:

```python
from src.database import DatabaseManager, ExpenseRecord

# Create expense
expense = ExpenseRecord(
    date="2024-03-13",
    merchant="Starbucks",
    category="food",
    amount=6.50
)

# Use database
with DatabaseManager() as db:
    db.insert_expense(expense)
    all_expenses = db.fetch_all_expenses()
    print(f"Total expenses: {len(all_expenses)}")
```

**Step 3:** Try it yourself with your own data

**Step 4:** Reference DATABASE_QUICK_REFERENCE.md for other operations

---

### Path 2: "I Want to Understand Everything"

**Step 1:** Read DATABASE_PROJECT_STRUCTURE.md (10 min)
- Understand file organization
- See all classes and methods

**Step 2:** Read DATABASE_MODULE.md (30 min)
- Complete architecture
- Full API reference
- All examples

**Step 3:** Review the code:
- `src/database/db_manager.py` - Main implementation
- `src/database/test_db_manager.py` - How it's tested
- `src/database/db_examples.py` - Usage examples

**Step 4:** Run the tests:
```bash
python -m pytest src/database/test_db_manager.py -v
```

---

### Path 3: "I Need to Integrate This"

**Step 1:** Read DATABASE_DELIVERY_SUMMARY.md (15 min)
- Understand integration requirements
- See integration examples

**Step 2:** Read the Integration section in DATABASE_MODULE.md

**Step 3:** Look at examples in `src/database/db_examples.py`

**Step 4:** Integrate into your workflow:
```python
# In your LangGraph workflow
from src.database import DatabaseManager, ExpenseRecord

def storage_node(state):
    db = DatabaseManager()
    for expense_data in state["expenses"]:
        expense = ExpenseRecord(**expense_data)
        db.insert_expense(expense)
    db.close()
    return state
```

---

## 🔑 Key Concepts

### ExpenseRecord - The Data Container

```python
from src.database import ExpenseRecord

# Create an expense record
expense = ExpenseRecord(
    date="2024-03-13",           # YYYY-MM-DD format
    merchant="Starbucks",        # Store name
    category="food & dining",    # Category
    amount=6.50,                 # Must be > 0
    notes="Morning coffee"        # Optional
)
```

**Validation Rules:**
- `merchant`: Cannot be empty
- `category`: Cannot be empty  
- `amount`: Must be > 0
- `date`: Must be YYYY-MM-DD format

---

### DatabaseManager - The Brain

```python
from src.database import DatabaseManager

# Initialize (creates database if needed)
db = DatabaseManager()

# Use it
db.insert_expense(expense)
expenses = db.fetch_all_expenses()

# Close it
db.close()

# Or use context manager (recommended)
with DatabaseManager() as db:
    db.insert_expense(expense)
    # Automatically closes
```

---

## 🎨 Common Use Cases

### Use Case 1: Simple Insert & Retrieve

```python
from src.database import DatabaseManager, ExpenseRecord

with DatabaseManager() as db:
    # Insert
    expense = ExpenseRecord(
        date="2024-03-13",
        merchant="Coffee Shop",
        category="food",
        amount=5.50
    )
    expense_id = db.insert_expense(expense)
    
    # Retrieve
    retrieved = db.fetch_expense_by_id(expense_id)
    print(f"Stored: {retrieved.merchant} - ${retrieved.amount}")
```

---

### Use Case 2: Bulk Import

```python
from src.database import DatabaseManager, ExpenseRecord

expenses = [
    ExpenseRecord(date="2024-03-01", merchant="Store1", category="food", amount=10),
    ExpenseRecord(date="2024-03-02", merchant="Store2", category="gas", amount=45),
    ExpenseRecord(date="2024-03-03", merchant="Store3", category="shop", amount=100),
]

with DatabaseManager() as db:
    ids = db.insert_expenses_batch(expenses)
    print(f"Imported {len(ids)} expenses")
```

---

### Use Case 3: Spending Analysis

```python
from src.database import DatabaseManager

with DatabaseManager() as db:
    # Get spending by category
    grouped = db.group_expenses_by_category()
    
    print("Spending by Category:")
    for category, data in sorted(grouped.items(), 
                                key=lambda x: x[1]['total'],
                                reverse=True):
        print(f"  {category}: ${data['total']:.2f} ({data['percentage']:.1f}%)")
    
    # Get overall statistics
    stats = db.get_summary_statistics()
    print(f"\nTotal: ${stats['total_spending']:.2f}")
    print(f"Average: ${stats['average_expense']:.2f}")
```

---

### Use Case 4: Budget Tracking

```python
from src.database import DatabaseManager

budget = {"food": 300, "gas": 200}

with DatabaseManager() as db:
    grouped = db.group_expenses_by_category()
    
    for category, limit in budget.items():
        actual = grouped.get(category, {}).get('total', 0)
        remaining = limit - actual
        status = "✓ OK" if remaining >= 0 else "✗ OVER"
        print(f"{category}: ${remaining:.2f} {status}")
```

---

### Use Case 5: Monthly Report

```python
from src.database import DatabaseManager

with DatabaseManager() as db:
    monthly = db.calculate_monthly_totals(year=2024)
    
    print("Monthly Spending 2024:")
    for month in sorted(monthly.keys()):
        print(f"  {month}: ${monthly[month]:.2f}")
```

---

## 📖 API Quick Reference

### Inserting Data

```python
# Single insert
expense_id = db.insert_expense(expense)

# Batch insert
ids = db.insert_expenses_batch([expense1, expense2, ...])
```

### Fetching Data

```python
# Get all
all = db.fetch_all_expenses()

# Get by ID
expense = db.fetch_expense_by_id(5)

# Get by date range
expenses = db.fetch_expenses_by_date_range("2024-03-01", "2024-03-31")

# Get by category
food = db.fetch_expenses_by_category("food")
```

### Analyzing Data

```python
# Monthly totals
monthly = db.calculate_monthly_totals(year=2024, month=3)

# Category breakdown
grouped = db.group_expenses_by_category()

# Overall stats
stats = db.get_summary_statistics()
```

### Modifying Data

```python
# Update
db.update_expense(expense_id, amount=10.00)

# Delete
db.delete_expense(expense_id)

# Delete all
db.delete_all_expenses()
```

---

## ⚠️ Important Rules

### Date Format

✅ **Correct:** `"2024-03-13"`  
❌ **Wrong:** `"03/13/2024"` or `"2024-3-13"`

```python
from datetime import datetime

# Get today in correct format
today = datetime.now().strftime("%Y-%m-%d")

expense = ExpenseRecord(date=today, ...)
```

### Amount Validation

✅ **Correct:** `6.50`, `100.00`, `0.01`  
❌ **Wrong:** `-5.00`, `0`, `0.00`

```python
# Amount must be positive
expense = ExpenseRecord(amount=6.50, ...)  # ✓
expense = ExpenseRecord(amount=-6.50, ...)  # ✗ Error!
```

### Required Fields

✅ **Must Provide:**
- `date` (YYYY-MM-DD)
- `merchant` (non-empty string)
- `category` (non-empty string)
- `amount` (> 0)

❌ **Cannot Omit:**
```python
# ✗ Error - missing merchant
ExpenseRecord(date="2024-03-13", category="food", amount=10)

# ✓ OK - all required fields
ExpenseRecord(date="2024-03-13", merchant="Store", category="food", amount=10)
```

---

## 🧪 Verifying Installation

Run this to verify everything works:

```python
from src.database import DatabaseManager, ExpenseRecord

# Test 1: Create database
db = DatabaseManager()
print("✓ Database created")

# Test 2: Create expense
expense = ExpenseRecord(
    date="2024-03-13",
    merchant="Test Store",
    category="test",
    amount=9.99
)
print("✓ Expense created")

# Test 3: Insert expense
expense_id = db.insert_expense(expense)
print(f"✓ Expense inserted (ID: {expense_id})")

# Test 4: Fetch expense
retrieved = db.fetch_expense_by_id(expense_id)
print(f"✓ Expense retrieved: {retrieved.merchant}")

# Test 5: Cleanup
db.delete_expense(expense_id)
db.close()
print("✓ Cleanup complete")

print("\n✅ All tests passed! Module is working correctly.")
```

---

## 🐛 Troubleshooting

### Problem: `ImportError: cannot import name 'DatabaseManager'`

**Solution:** Make sure you're in the correct directory and use:
```python
from src.database import DatabaseManager
```

---

### Problem: `ValueError: merchant cannot be empty`

**Solution:** Provide a non-empty merchant name:
```python
# ✓ Correct
ExpenseRecord(merchant="Starbucks", ...)

# ✗ Wrong
ExpenseRecord(merchant="", ...)
```

---

### Problem: `ValueError: Invalid date format`

**Solution:** Use YYYY-MM-DD format:
```python
from datetime import datetime

# ✓ Correct
date = datetime.now().strftime("%Y-%m-%d")

# ✗ Wrong
date = "03/13/2024"
```

---

### Problem: `ValueError: amount must be > 0`

**Solution:** Use a positive amount:
```python
# ✓ Correct
amount = 6.50

# ✗ Wrong
amount = -6.50  # or 0
```

---

## 📚 What to Read Next

### For Quick Reference
**→** `DATABASE_QUICK_REFERENCE.md`

### For Complete Details
**→** `DATABASE_MODULE.md`

### For Project Structure
**→** `DATABASE_PROJECT_STRUCTURE.md`

### For Examples
**→** `src/database/db_examples.py`

### For Tests
**→** `src/database/test_db_manager.py`

---

## ✅ Checklist: You're Ready When...

- [ ] You've read this file
- [ ] You understand the 3 use cases
- [ ] You know the date format (YYYY-MM-DD)
- [ ] You know the required fields
- [ ] You can create an ExpenseRecord
- [ ] You can insert an expense
- [ ] You can fetch expenses
- [ ] You know how to use context manager

---

## 🎯 Next Steps

### If You Want to...

**Use it immediately:**
→ Copy code from Use Cases section (above)

**Understand it deeply:**
→ Read `DATABASE_MODULE.md`

**See it in action:**
→ Run `src/database/db_examples.py`

**Integrate it:**
→ Read "Integration" section in `DATABASE_MODULE.md`

**Test it:**
→ Run `pytest src/database/test_db_manager.py -v`

---

## 💡 Pro Tips

### Tip 1: Use Context Manager

```python
# ✓ Recommended - auto-closes
with DatabaseManager() as db:
    db.insert_expense(expense)

# ✗ Risky - manual close
db = DatabaseManager()
db.insert_expense(expense)
db.close()  # Easy to forget!
```

### Tip 2: Batch Insert for Multiple Records

```python
# ✓ Fast - one transaction
ids = db.insert_expenses_batch(expenses)

# ✗ Slow - separate transactions
for expense in expenses:
    db.insert_expense(expense)
```

### Tip 3: Fetch Specific Data

```python
# ✓ Efficient - only what you need
food = db.fetch_expenses_by_category("food")

# ✗ Inefficient - fetch all, filter locally
all = db.fetch_all_expenses()
food = [e for e in all if e.category == "food"]
```

### Tip 4: Handle Errors Properly

```python
# ✓ Good error handling
try:
    db.insert_expense(expense)
except ValueError as e:
    print(f"Invalid data: {e}")
except Exception as e:
    print(f"Database error: {e}")

# ✗ No error handling
db.insert_expense(expense)
```

---

## 📞 Questions?

### Quick Questions
→ See `DATABASE_QUICK_REFERENCE.md`

### Technical Questions
→ See `DATABASE_MODULE.md` → Troubleshooting

### Integration Questions
→ See `DATABASE_MODULE.md` → Integration

### Example Code
→ See `src/database/db_examples.py`

---

## 🎓 Learning Path

```
START (You are here)
    ↓
[5 min]  DATABASE_QUICK_REFERENCE.md
    ↓
[10 min] This file - Practice basic usage
    ↓
[15 min] DATABASE_PROJECT_STRUCTURE.md
    ↓
[30 min] DATABASE_MODULE.md - Full details
    ↓
[30 min] src/database/db_examples.py - Run examples
    ↓
[60 min] Read the code: db_manager.py, test_db_manager.py
    ↓
[Now]    Ready to integrate and use!
```

---

## ✨ Key Takeaways

1. **DatabaseManager** handles all database operations
2. **ExpenseRecord** is the data structure for expenses
3. **Use context manager** for automatic cleanup
4. **Follow the rules** (date format, amount > 0, etc.)
5. **Read the docs** when you get stuck
6. **Run the examples** to see it in action

---

## 🚀 Ready to Start?

### Option 1: Quick Start (5 minutes)
```python
from src.database import DatabaseManager, ExpenseRecord

with DatabaseManager() as db:
    expense = ExpenseRecord(
        date="2024-03-13",
        merchant="Starbucks",
        category="food",
        amount=6.50
    )
    db.insert_expense(expense)
```

### Option 2: Learn More
→ Read `DATABASE_QUICK_REFERENCE.md`

### Option 3: Deep Dive
→ Read `DATABASE_MODULE.md`

---

## 📊 Module Status

✅ **Production Ready**  
✅ **Fully Tested** (33+ tests)  
✅ **Fully Documented** (1,300+ lines)  
✅ **Type Safe** (100% type hints)  
✅ **Ready to Use**

---

**Happy Coding! 🎉**

---

**Last Updated:** March 2024  
**Status:** Production Ready  
**Version:** 1.0.0
