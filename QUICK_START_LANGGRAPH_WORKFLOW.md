# LangGraph Workflow Quick Start

**Get the FinSight AI LangGraph workflow running in 5 minutes**

---

## ⚡ 60-Second Example

```python
from src.workflows import FinSightWorkflow

# Initialize
workflow = FinSightWorkflow(use_llm=False)

# Process receipt
result = workflow.run(
    input_type="text",
    input_content="""
    Starbucks
    Latte - $6.50
    Croissant - $4.20
    
    Whole Foods
    Milk - $5.99
    Bread - $4.50
    """
)

# Get results
print(f"Total: ${result.analysis.total_spending:.2f}")
print(f"Categories: {len(result.analysis.category_breakdown)}")
print(result.analysis.summary)
```

**Output:**
```
Total: $21.19
Categories: 2
Category Breakdown:
  Food: $21.19 (100.0%) - 4 items
```

---

## 📦 Installation

```bash
# Install langgraph (if not already installed)
pip install langgraph langchain

# Or update all requirements
pip install -r requirements.txt
```

---

## 🎯 5 Common Tasks

### Task 1: Process Text Receipt

```python
from src.workflows import FinSightWorkflow

workflow = FinSightWorkflow()
result = workflow.run(
    input_type="text",
    input_content="Starbucks $6.50\nGroceries $25.00"
)

print(f"Total: ${result.analysis.total_spending:.2f}")
```

### Task 2: Process Image Receipt

```python
result = workflow.run(
    input_type="image",
    input_content="path/to/receipt.jpg"
)

print(f"Extracted: {len(result.extracted_text)} characters")
print(f"Items: {len(result.categorized_expenses)}")
```

### Task 3: With Budget Limits

```python
result = workflow.run(
    input_type="text",
    input_content=receipt_text,
    budget_limits={
        "food": 300,
        "transport": 150,
        "shopping": 200
    }
)

# Check if over budget
for cat in result.analysis.category_breakdown:
    budget = result.budget_limits.get(cat.category)
    if budget and cat.amount > budget:
        print(f"⚠️  {cat.category} over budget!")
```

### Task 4: Get Recommendations

```python
result = workflow.run(input_type="text", input_content=text)

print("Cost-Saving Recommendations:")
for rec in result.recommendations:
    print(f"  • {rec.title}")
    print(f"    Save: ${rec.potential_savings:.2f}/month")
    print(f"    Priority: {rec.priority}")
```

### Task 5: Export to JSON

```python
import json

result = workflow.run(input_type="text", input_content=text)

# Convert to JSON
json_data = json.dumps(result.to_dict(), indent=2)

# Save to file
with open("result.json", "w") as f:
    f.write(json_data)
```

---

## 🏗️ Workflow Nodes

The workflow consists of **6 sequential nodes**:

```
Input
  ↓
1. OCR Node         → Extract text from image or accept text
  ↓
2. Extraction Node  → Parse text into expense items
  ↓
3. Categorization Node → Assign categories
  ↓
4. Storage Node     → Save to database
  ↓
5. Analysis Node    → Generate spending insights
  ↓
6. Recommendations Node → Create recommendations
  ↓
Output (WorkflowState)
```

---

## 📊 Workflow State

The `WorkflowState` object carries data through all nodes:

```python
state.input_type              # "text" or "image"
state.input_content           # Your input

state.extracted_text          # Text from OCR
state.raw_items              # Parsed items
state.categorized_expenses   # Items with categories
state.storage_id             # Database ID
state.analysis               # Analysis results
state.recommendations        # Cost-saving tips

state.workflow_id            # Unique ID
state.created_at             # Start time
state.completed_at           # End time
state.processing_time_ms     # Total time
```

---

## 🔍 Access Results

### Analysis Results

```python
result = workflow.run(input_type="text", input_content=text)

# Total spending
print(f"Total: ${result.analysis.total_spending:.2f}")

# By category
for cat in result.analysis.category_breakdown:
    print(f"{cat.category}: ${cat.amount:.2f} ({cat.percentage:.1f}%)")

# Highest spending
print(f"Highest: {result.analysis.highest_spending_category}")

# Summary
print(result.analysis.summary)
```

### Expense Items

```python
for item in result.categorized_expenses:
    print(f"{item.merchant}: ${item.amount:.2f} ({item.category})")
```

### Recommendations

```python
for rec in result.recommendations:
    print(f"{rec.title}")
    print(f"  Description: {rec.description}")
    print(f"  Save: ${rec.potential_savings:.2f}")
    print(f"  Priority: {rec.priority}")
    for step in rec.actionable_steps:
        print(f"    - {step}")
```

---

## ⚙️ Configuration

### Keyword Mode (Default)

```python
workflow = FinSightWorkflow(use_llm=False)
# Fast, no setup needed
```

### LLM Mode

```python
workflow = FinSightWorkflow(use_llm=True)
# Better accuracy, requires Ollama
```

### Custom Database

```python
workflow = FinSightWorkflow(db_path="my_data.db")
```

### In-Memory (Testing)

```python
workflow = FinSightWorkflow(db_path=":memory:")
```

---

## 🚨 Error Handling

### Check for Errors

```python
result = workflow.run(input_type="text", input_content="")

if result.has_error():
    print("Errors occurred:")
    for error in result.get_errors():
        print(f"  - {error}")
```

### Completion Status

```python
if result.is_complete():
    print("✅ Workflow completed successfully")
else:
    print("❌ Workflow failed or incomplete")
    print(f"Processing time: {result.processing_time_ms:.2f}ms")
```

---

## 💾 Database Access

The workflow automatically saves to SQLite database with 3 tables:

### Query Receipts
```python
import sqlite3

conn = sqlite3.connect("finsight.db")
cursor = conn.cursor()

# Get all receipts
cursor.execute("SELECT * FROM receipts")
for row in cursor.fetchall():
    print(row)

conn.close()
```

### Query Expenses
```python
cursor.execute("""
    SELECT merchant, amount, category 
    FROM expenses 
    WHERE category = 'food'
""")
```

### Query Analyses
```python
cursor.execute("""
    SELECT analysis_json 
    FROM analyses 
    LIMIT 1
""")

import json
analysis = json.loads(cursor.fetchone()[0])
print(analysis)
```

---

## 📈 Performance Tips

### Speed Optimization

```python
# Keyword mode is fastest
workflow = FinSightWorkflow(use_llm=False)  # ~200ms

# LLM mode is more accurate but slower
workflow = FinSightWorkflow(use_llm=True)   # ~2-5s
```

### Batch Processing

```python
workflow = FinSightWorkflow(use_llm=False)

total = 0
for receipt in receipts:
    result = workflow.run(input_type="text", input_content=receipt)
    total += result.analysis.total_spending

print(f"Total: ${total:.2f}")
```

---

## 🧪 Run Examples

```bash
# Run all examples
python examples/langgraph_workflow_examples.py

# Output examples:
# - Example 1: Text input processing
# - Example 2: With budget limits
# - Example 3: Multiple receipts
# - Example 4: JSON export
# - Example 5: Workflow diagnostics
# - Example 6: State inspection
# - Example 7: Mode comparison
```

---

## 🔗 Integration

### With REST API

```python
from fastapi import FastAPI
from src.workflows import FinSightWorkflow

app = FastAPI()
workflow = FinSightWorkflow()

@app.post("/process")
def process(text: str):
    result = workflow.run(input_type="text", input_content=text)
    return result.to_dict()
```

### With Database

```python
result = workflow.run(input_type="text", input_content=text)
# Automatically saved to finsight.db
```

### With CLI

```bash
python -c "
from src.workflows import FinSightWorkflow
w = FinSightWorkflow()
r = w.run('text', 'Starbucks \$6.50')
print(f'Total: \${r.analysis.total_spending}')
"
```

---

## 📋 Troubleshooting

### Import Error: langgraph

```bash
# Install langgraph
pip install langgraph
```

### No Text Extracted

**For text input:**
- Ensure text is not empty

**For image input:**
- Ensure image file exists
- Check image quality
- Verify file path

### No Recommendations

- Spending might be below threshold
- Check categorization worked
- Verify items were found

### Database Error

```python
# Use in-memory database for testing
workflow = FinSightWorkflow(db_path=":memory:")
```

---

## ✅ Checklist

- ✅ Installed langgraph
- ✅ Created FinSightWorkflow instance
- ✅ Ran first workflow
- ✅ Accessed results
- ✅ Checked for errors
- ✅ Explored all nodes
- ✅ Tried budget limits
- ✅ Exported to JSON

---

## 🎯 Next Steps

1. **Run Examples:** `python examples/langgraph_workflow_examples.py`
2. **Read Docs:** [LANGGRAPH_WORKFLOW.md](LANGGRAPH_WORKFLOW.md)
3. **Explore Code:** Check `src/workflows/workflow.py`
4. **Integrate:** Use in your application
5. **Customize:** Modify for your needs

---

## 📚 Related Documentation

- **Full Docs:** [LANGGRAPH_WORKFLOW.md](LANGGRAPH_WORKFLOW.md)
- **Examples:** [examples/langgraph_workflow_examples.py](examples/langgraph_workflow_examples.py)
- **API Reference:** Check `src/workflows/` source code

---

**Ready to use the workflow!** 🚀

Try the 60-second example above to get started.
