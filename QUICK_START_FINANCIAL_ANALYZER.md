# Financial Analysis AI Module - Quick Start Guide

**⏱️ 5-minute quick start** | Full docs: `docs/FINANCIAL_ANALYZER.md`

---

## 60-Second Example

```python
from src.agents import FinancialAnalyzer

# Create analyzer
analyzer = FinancialAnalyzer(use_llm=False)

# Analyze expenses
expenses = [
    {"merchant": "Starbucks", "amount": 8.20, "category": "food"},
    {"merchant": "Uber", "amount": 18.00, "category": "transport"},
    {"merchant": "Amazon", "amount": 42.00, "category": "shopping"}
]

analysis = analyzer.analyze(expenses)

# Print summary
print(analysis.summary)

# Output:
# Total Spending: $68.20
# 
# Category Breakdown:
#   Shopping: $42.00 (61.6%) - 1 items
#   Transport: $18.00 (26.4%) - 1 items
#   Food: $8.20 (12.0%) - 1 items
```

---

## Installation

```bash
pip install -r requirements.txt
```

---

## 5 Common Tasks

### Task 1: Get Total Spending

```python
from src.agents import FinancialAnalyzer

analyzer = FinancialAnalyzer(use_llm=False)
analysis = analyzer.analyze(expenses)

print(f"Total: ${analysis.total_spending:.2f}")
print(f"Expenses: {analysis.expense_count}")
```

### Task 2: See Category Breakdown

```python
analysis = analyzer.analyze(expenses)

print("Category Breakdown:")
for cat in analysis.category_breakdown:
    print(f"  {cat.category}: ${cat.amount:.2f} ({cat.count} items)")
```

### Task 3: Find Highest Spending Area

```python
analysis = analyzer.analyze(expenses)

print(f"Highest: {analysis.highest_spending_category}")
print(f"Amount: ${analysis.highest_spending_amount:.2f}")
```

### Task 4: Get Cost-Saving Recommendations

```python
analysis = analyzer.analyze(expenses)

print("Recommendations:")
for rec in analysis.recommendations:
    print(f"  • {rec.title}")
    print(f"    Save: ${rec.potential_savings:.2f}/month")
    print(f"    Priority: {rec.priority}")
```

### Task 5: Export as JSON

```python
import json

analysis = analyzer.analyze(expenses)
json_output = json.dumps(analysis.to_dict(), indent=2)
print(json_output)

# Or save to file
with open("analysis.json", "w") as f:
    json.dump(analysis.to_dict(), f)
```

---

## Modes

### Keyword Mode (Recommended First)

```python
# No setup required
analyzer = FinancialAnalyzer(use_llm=False)
analysis = analyzer.analyze(expenses)

# Characteristics:
# - No external dependencies
# - Instant (< 1ms)
# - Offline
# - Good accuracy (85-90%)
```

### LLM Mode (Better Accuracy)

```python
# Requires: ollama serve running
analyzer = FinancialAnalyzer(use_llm=True)
analysis = analyzer.analyze(expenses)

# Characteristics:
# - Needs Ollama (free, local)
# - Slower (500ms-2s)
# - Better recommendations
# - Higher accuracy (90-95%)
```

### Auto Mode (Smart)

```python
# Uses LLM if available, falls back to keywords
analyzer = FinancialAnalyzer(use_llm=True, use_fallback=True)
analysis = analyzer.analyze(expenses)
```

---

## Enable LLM (Optional)

```bash
# Install Ollama
brew install ollama

# Start Ollama
ollama serve

# Pull a model
ollama pull mistral

# Now use with LLM
analyzer = FinancialAnalyzer(use_llm=True)
```

---

## Input Format

Expenses must be a list of dictionaries:

```python
expenses = [
    {
        "merchant": "Store Name",      # Required
        "amount": 25.50,               # Required (float or int)
        "category": "shopping",        # Required
        "currency": "USD"              # Optional (defaults to USD)
    },
    # ...
]
```

### Supported Categories

```
food, groceries, transport, shopping, subscriptions,
utilities, entertainment, healthcare, other
```

---

## Output Format

### Summary (Human-Readable)

```python
print(analysis.summary)

# Output:
# Total Spending: $420.50
# 
# Category Breakdown:
#   Shopping: $150.00 (35.7%) - 2 items
#   Food: $120.00 (28.5%) - 10 items
#   Transport: $90.00 (21.4%) - 5 items
#   Subscriptions: $60.50 (14.4%) - 3 items
# 
# Top Recommendations:
#   1. Reduce Online Shopping (HIGH)
#      Potential savings: $45.00/month
#   2. Optimize Transportation (MEDIUM)
#      Potential savings: $13.50/month
```

### Dictionary (JSON-Ready)

```python
analysis.to_dict()

# Returns:
# {
#   'total_spending': 420.50,
#   'currency': 'USD',
#   'expense_count': 20,
#   'category_breakdown': [
#     {'category': 'shopping', 'amount': 150.0, 'count': 2, 'average': 75.0, 'percentage': 35.7},
#     ...
#   ],
#   'recommendations': [
#     {'title': '...', 'description': '...', 'potential_savings': 45.0, ...},
#     ...
#   ],
#   'summary': '...'
# }
```

---

## Common Patterns

### Weekly Analysis

```python
# Analyze a week of expenses
weekly_expenses = [...]
weekly_analysis = analyzer.analyze(weekly_expenses)

# Project to monthly
monthly_projection = weekly_analysis.total_spending * 4.33
print(f"Monthly estimate: ${monthly_projection:.2f}")
```

### Budget Compliance

```python
# Check if over budget
budget_limits = {"food": 300, "shopping": 200}
analysis = analyzer.analyze(expenses, budget_limits=budget_limits)

# See if categories are over
for cat in analysis.category_breakdown:
    budget = budget_limits.get(cat.category)
    if budget and cat.amount > budget:
        over = cat.amount - budget
        print(f"⚠️ {cat.category}: ${over:.2f} over budget")
```

### Category Comparison

```python
# Compare spending across categories
analysis = analyzer.analyze(expenses)

# Sort by amount
sorted_cats = sorted(analysis.category_breakdown, 
                     key=lambda x: x.amount, reverse=True)

for cat in sorted_cats:
    print(f"{cat.category.title()}: ${cat.amount:.2f} ({cat.percentage:.1f}%)")
```

### Spending Trends

```python
# Compare two periods
period1 = analyzer.analyze(expenses_week1)
period2 = analyzer.analyze(expenses_week2)

difference = period2.total_spending - period1.total_spending
percentage = (difference / period1.total_spending) * 100

if difference > 0:
    print(f"Spending increased by ${difference:.2f} ({percentage:+.1f}%)")
else:
    print(f"Spending decreased by ${-difference:.2f} ({percentage:.1f}%)")
```

---

## Tips

1. **Use keyword mode first** - No setup needed, fast results
2. **Add budget limits** - Get smarter recommendations
3. **Review regularly** - Weekly analysis shows patterns
4. **Act on recommendations** - Focus on high-priority items
5. **Track progress** - Compare periods to see improvement

---

## Troubleshooting

### No Recommendations?
- Spending might be below threshold
- Check category values match
- Try keyword mode explicitly

### LLM Not Working?
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull a model
ollama pull mistral
```

### Wrong Results?
- Verify expense amounts
- Check category names (use lowercase)
- Ensure merchant field is present

---

## Next Steps

- 📖 **Full Documentation:** [docs/FINANCIAL_ANALYZER.md](docs/FINANCIAL_ANALYZER.md)
- 💻 **More Examples:** [examples/financial_analyzer_examples.py](examples/financial_analyzer_examples.py)
- 🧪 **Tests:** [src/agents/test_financial_analyzer.py](src/agents/test_financial_analyzer.py)

---

## Quick Reference

```python
from src.agents import FinancialAnalyzer, analyze_expenses_financial

# Basic analysis
analyzer = FinancialAnalyzer(use_llm=False)
analysis = analyzer.analyze(expenses)

# Quick convenience function
result = analyze_expenses_financial(expenses, use_llm=False)

# With budget limits
analysis = analyzer.analyze(expenses, budget_limits={"food": 300})

# Get recommendations
for rec in analysis.recommendations:
    print(f"{rec.title}: Save ${rec.potential_savings:.2f}")

# Export
import json
json.dump(analysis.to_dict(), open("analysis.json", "w"))
```

---

**Ready to use!** Pick an example above and get started. 🚀

**Full Documentation:** [docs/FINANCIAL_ANALYZER.md](docs/FINANCIAL_ANALYZER.md)
