# LangGraph Workflow - Navigation & Quick Links

## 📚 Documentation

### Core Documentation Files
| File | Purpose | Read Time |
|------|---------|-----------|
| **LANGGRAPH_WORKFLOW_SUMMARY.md** | Executive summary | 5 min |
| **QUICK_START_LANGGRAPH_WORKFLOW.md** | Get started quickly | 5 min |
| **LANGGRAPH_WORKFLOW.md** | Complete API reference | 30 min |

---

## 🔧 Source Code

### Main Workflow Implementation
```
src/workflows/
├── __init__.py           Module exports
├── state.py              State schema & dataclasses (250 lines)
├── workflow.py           FinSightWorkflow orchestrator (450 lines)
└── test_workflow.py      Test suite with 27+ tests (450 lines)
```

### Quick File Guide

**state.py** - Start here to understand data structures
- `ExpenseItem` - Single expense
- `Recommendation` - Cost-saving tip
- `AnalysisResult` - Financial analysis
- `WorkflowState` - Central state object

**workflow.py** - The orchestrator
- `FinSightWorkflow` - Main class
- `_ocr_node()` - Text extraction
- `_extraction_node()` - Item parsing
- `_categorization_node()` - Category assignment
- `_storage_node()` - Database persistence
- `_analysis_node()` - Financial insights
- `_recommendations_node()` - Recommendations

**test_workflow.py** - Test suite
- 27+ test cases
- Tests for all state classes
- Integration tests
- Performance tests

---

## 💡 Examples

### Example File
**examples/langgraph_workflow_examples.py** (450+ lines)

7 complete, runnable examples:
1. **example_1_text_input()** - Basic text processing
2. **example_2_with_budget_limits()** - Budget checking
3. **example_3_multiple_receipts()** - Batch processing
4. **example_4_json_output()** - JSON export
5. **example_5_workflow_diagnostics()** - Error handling
6. **example_6_state_inspection()** - State debugging
7. **example_7_config_comparison()** - Mode comparison

### Run All Examples
```bash
python examples/langgraph_workflow_examples.py
```

---

## 🧪 Testing

### Run Tests
```bash
# All tests
python -m pytest src/workflows/test_workflow.py -v

# Specific test class
python -m pytest src/workflows/test_workflow.py::TestWorkflowState -v

# Specific test
python -m pytest src/workflows/test_workflow.py::TestFinSightWorkflow::test_workflow_text_input -v

# With coverage
python -m pytest src/workflows/test_workflow.py --cov=src.workflows
```

### Test Overview
- **27+ test cases**
- **7 test classes**
- **100% dataclass coverage**
- **Integration & performance tests**

---

## 🚀 Getting Started

### Step 1: Read Quick Start (5 min)
```bash
cat QUICK_START_LANGGRAPH_WORKFLOW.md
```

### Step 2: Run Examples (5 min)
```bash
python examples/langgraph_workflow_examples.py
```

### Step 3: Run Tests (2 min)
```bash
python -m pytest src/workflows/test_workflow.py -v
```

### Step 4: Use in Code
```python
from src.workflows import FinSightWorkflow

workflow = FinSightWorkflow()
result = workflow.run("text", "Starbucks $6.50\nWhole Foods $15.99")
print(f"Total: ${result.analysis.total_spending:.2f}")
```

---

## 📖 Learning Path

### Beginner (30 min)
1. Read LANGGRAPH_WORKFLOW_SUMMARY.md
2. Run examples
3. Try simple text input

### Intermediate (1 hour)
1. Read QUICK_START_LANGGRAPH_WORKFLOW.md
2. Study workflow.py structure
3. Run all examples
4. Check test cases

### Advanced (2 hours)
1. Read LANGGRAPH_WORKFLOW.md
2. Study state.py in detail
3. Study workflow.py implementations
4. Understand node interactions
5. Review error handling

### Expert (1 day)
1. Modify examples for your use cases
2. Extend state schema if needed
3. Add custom nodes
4. Integrate with your systems
5. Deploy and monitor

---

## 🎯 Common Tasks

### Process a Text Receipt
**File:** QUICK_START_LANGGRAPH_WORKFLOW.md (Task 1)
**Example:** examples/langgraph_workflow_examples.py::example_1_text_input

```python
workflow = FinSightWorkflow()
result = workflow.run("text", "Starbucks $6.50")
```

### Process an Image
**File:** LANGGRAPH_WORKFLOW.md (Input Handling section)
**Example:** examples/langgraph_workflow_examples.py::example_1_text_input

```python
result = workflow.run("image", "/path/to/receipt.jpg")
```

### Check Budget Compliance
**File:** QUICK_START_LANGGRAPH_WORKFLOW.md (Task 2)
**Example:** examples/langgraph_workflow_examples.py::example_2_with_budget_limits

```python
result = workflow.run(
    "text", receipt,
    budget_limits={"food": 300, "shopping": 200}
)
```

### Process Multiple Receipts
**File:** QUICK_START_LANGGRAPH_WORKFLOW.md (Task 3)
**Example:** examples/langgraph_workflow_examples.py::example_3_multiple_receipts

```python
for receipt in receipts:
    result = workflow.run("text", receipt)
```

### Export to JSON
**File:** QUICK_START_LANGGRAPH_WORKFLOW.md (Task 4)
**Example:** examples/langgraph_workflow_examples.py::example_4_json_output

```python
import json
json_data = json.dumps(result.to_dict(), indent=2)
```

### Debug Errors
**File:** LANGGRAPH_WORKFLOW.md (Error Handling section)
**Example:** examples/langgraph_workflow_examples.py::example_5_workflow_diagnostics

```python
if result.has_error():
    for error in result.get_errors():
        print(f"Error: {error}")
```

---

## 🔍 Finding Things

### I want to...

**Understand the architecture**
→ LANGGRAPH_WORKFLOW_SUMMARY.md (Architecture section)
→ LANGGRAPH_WORKFLOW.md (Overview section)

**Get started quickly**
→ QUICK_START_LANGGRAPH_WORKFLOW.md

**See working code**
→ examples/langgraph_workflow_examples.py

**Understand state management**
→ src/workflows/state.py
→ LANGGRAPH_WORKFLOW.md (State section)

**Learn the node implementations**
→ src/workflows/workflow.py

**See how to test**
→ src/workflows/test_workflow.py

**Configure the workflow**
→ LANGGRAPH_WORKFLOW.md (Configuration section)

**Understand performance**
→ LANGGRAPH_WORKFLOW.md (Performance section)

**Integrate with my system**
→ LANGGRAPH_WORKFLOW.md (Integration section)

**Handle errors properly**
→ LANGGRAPH_WORKFLOW.md (Error Handling section)

**Access the database**
→ LANGGRAPH_WORKFLOW.md (Database section)

**Compare LLM vs Keyword mode**
→ examples/langgraph_workflow_examples.py::example_7_config_comparison

---

## 📊 Project Structure

```
FinSight AI/
├── src/
│   ├── workflows/                   NEW: LangGraph Workflow
│   │   ├── __init__.py
│   │   ├── state.py                (250 lines)
│   │   ├── workflow.py             (450 lines)
│   │   └── test_workflow.py        (450 lines)
│   ├── modules/                     Existing 4 modules
│   │   ├── ocr/
│   │   ├── parser/
│   │   ├── categorizer/
│   │   └── analyzer/
│   └── ...
├── examples/
│   ├── langgraph_workflow_examples.py  (NEW: 450 lines)
│   └── ...
├── LANGGRAPH_WORKFLOW_SUMMARY.md       (NEW: Summary)
├── QUICK_START_LANGGRAPH_WORKFLOW.md   (NEW: Quick Start)
├── LANGGRAPH_WORKFLOW.md               (NEW: Complete Docs)
├── WORKFLOW_NAVIGATION.md              (NEW: This file)
└── ...
```

---

## 🔗 External Links

### LangGraph Documentation
- Official: https://python.langchain.com/docs/langgraph
- StateGraph: https://python.langchain.com/docs/langgraph/concepts#stategraph

### Dependencies
- langchain: https://python.langchain.com
- langgraph: https://github.com/langchain-ai/langgraph
- Pydantic: https://docs.pydantic.dev

---

## ⚡ Quick Command Reference

```bash
# Run examples
python examples/langgraph_workflow_examples.py

# Run all tests
python -m pytest src/workflows/test_workflow.py -v

# Run specific test
python -m pytest src/workflows/test_workflow.py::TestFinSightWorkflow -v

# Run with coverage
python -m pytest src/workflows/test_workflow.py --cov=src.workflows

# View documentation
cat QUICK_START_LANGGRAPH_WORKFLOW.md
cat LANGGRAPH_WORKFLOW.md
cat LANGGRAPH_WORKFLOW_SUMMARY.md

# Use in Python
from src.workflows import FinSightWorkflow
```

---

## 💾 File Size Reference

| File | Size | Purpose |
|------|------|---------|
| state.py | 250 lines | Data structures |
| workflow.py | 450 lines | Orchestration |
| test_workflow.py | 450 lines | Tests |
| examples | 450 lines | 7 examples |
| LANGGRAPH_WORKFLOW.md | 600 lines | Complete docs |
| QUICK_START_LANGGRAPH_WORKFLOW.md | 350 lines | Quick start |
| LANGGRAPH_WORKFLOW_SUMMARY.md | 200 lines | Summary |
| **Total** | **2,750 lines** | Complete system |

---

## 📌 Key Files to Remember

1. **src/workflows/workflow.py** - The main orchestrator (450 lines)
2. **QUICK_START_LANGGRAPH_WORKFLOW.md** - Get started (5 min)
3. **examples/langgraph_workflow_examples.py** - 7 working examples
4. **LANGGRAPH_WORKFLOW.md** - Complete reference

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Python environment configured
- [ ] langgraph installed (`pip install langgraph>=0.0.44`)
- [ ] Run examples: `python examples/langgraph_workflow_examples.py`
- [ ] All tests pass: `python -m pytest src/workflows/test_workflow.py -v`
- [ ] Can import: `from src.workflows import FinSightWorkflow`
- [ ] Create and run simple workflow
- [ ] Check database was created
- [ ] Review generated JSON output

---

## 🎓 Next Steps

1. ✅ Read LANGGRAPH_WORKFLOW_SUMMARY.md (5 min)
2. ✅ Run examples (5 min)
3. ✅ Run tests (2 min)
4. ⭐ Try with your own data
5. 🚀 Integrate into your application

---

**Created:** March 13, 2024  
**Status:** ✅ Complete and Ready to Use  
**Questions?** Check LANGGRAPH_WORKFLOW.md troubleshooting section
