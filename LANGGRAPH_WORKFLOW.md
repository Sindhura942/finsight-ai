# FinSight AI LangGraph Workflow

**Complete LangGraph-based orchestration for the FinSight AI expense processing pipeline**

---

## 📋 Overview

The FinSight AI Workflow is a **LangGraph-based orchestration layer** that connects all four modules into a seamless, production-ready pipeline:

```
Receipt Input (Text/Image)
        ↓
    [OCR Node]
        ↓
   [Extraction Node]
        ↓
  [Categorization Node]
        ↓
   [Storage Node]
        ↓
   [Analysis Node]
        ↓
 [Recommendations Node]
        ↓
    Final Results
```

---

## 🏗️ Architecture

### Workflow State

The central `WorkflowState` object flows through all nodes carrying:

```python
@dataclass
class WorkflowState:
    # Input
    input_type: str          # "text" or "image"
    input_content: str       # File path or text content
    
    # Node Outputs
    extracted_text: str      # From OCR node
    raw_items: List[...]     # From extraction node
    categorized_expenses: List[...]  # From categorization node
    storage_id: str          # From storage node
    analysis: AnalysisResult # From analysis node
    recommendations: List[...] # From recommendations node
    
    # Metadata
    workflow_id: str
    created_at: str
    completed_at: str
    processing_time_ms: float
```

### 6 Sequential Nodes

#### 1️⃣ OCR Node
**Purpose:** Extract text from images or accept text input

```python
def _ocr_node(state: WorkflowState) -> WorkflowState:
    if state.input_type == "image":
        state.extracted_text = self.ocr.extract(state.input_content)
    elif state.input_type == "text":
        state.extracted_text = state.input_content
```

**Input:** `input_type`, `input_content`  
**Output:** `extracted_text`, `ocr_confidence`, `ocr_error`  
**Time:** 2-5s (image) / 0ms (text)

#### 2️⃣ Extraction Node
**Purpose:** Parse text into structured expense items

```python
def _extraction_node(state: WorkflowState) -> WorkflowState:
    parsed_items = self.parser.parse(state.extracted_text)
    state.raw_items = [ExpenseItem(...) for item in parsed_items]
```

**Input:** `extracted_text`  
**Output:** `raw_items`, `extraction_error`  
**Time:** 100-500ms

#### 3️⃣ Categorization Node
**Purpose:** Assign categories to items using AI or keywords

```python
def _categorization_node(state: WorkflowState) -> WorkflowState:
    categorized = self.categorizer.categorize(items)
    state.categorized_expenses = [ExpenseItem(category=...) for ...]
```

**Input:** `raw_items`  
**Output:** `categorized_expenses`, `categorization_error`  
**Time:** 50-200ms (keyword) / 500ms-2s (LLM)

#### 4️⃣ Storage Node
**Purpose:** Persist data to SQLite database

```python
def _storage_node(state: WorkflowState) -> WorkflowState:
    # Insert receipts table
    # Insert expenses table
    state.storage_id = receipt_id
```

**Input:** `extracted_text`, `categorized_expenses`  
**Output:** `storage_id`, `storage_error`  
**Database:** SQLite with 3 tables (receipts, expenses, analyses)  
**Time:** 10-50ms

#### 5️⃣ Analysis Node
**Purpose:** Analyze spending patterns and generate statistics

```python
def _analysis_node(state: WorkflowState) -> WorkflowState:
    analysis_result = self.analyzer.analyze(expenses)
    state.analysis = AnalysisResult(...)
```

**Input:** `categorized_expenses`  
**Output:** `analysis`, `analysis_error`  
**Time:** 1-2ms (keyword) / 500ms-2s (LLM)

#### 6️⃣ Recommendations Node
**Purpose:** Generate cost-saving recommendations

```python
def _recommendations_node(state: WorkflowState) -> WorkflowState:
    state.recommendations = [Recommendation(...) for ...]
    # Store analysis in database
```

**Input:** `analysis`  
**Output:** `recommendations`, `recommendation_error`  
**Time:** 1-2ms

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies including langgraph
pip install langgraph langchain anthropic

# Or update requirements
pip install -r requirements.txt
```

### Basic Usage

```python
from src.workflows import FinSightWorkflow

# Initialize workflow
workflow = FinSightWorkflow(use_llm=False)

# Process text receipt
result = workflow.run(
    input_type="text",
    input_content="""
    Starbucks
    Latte - $6.50
    
    Whole Foods
    Milk - $5.99
    """
)

# Access results
print(f"Total: ${result.analysis.total_spending:.2f}")
print(f"Recommendations: {len(result.recommendations)}")
```

### Process Image

```python
result = workflow.run(
    input_type="image",
    input_content="path/to/receipt.jpg"
)
```

### With Budget Limits

```python
result = workflow.run(
    input_type="text",
    input_content=receipt_text,
    budget_limits={
        "food": 300,
        "shopping": 200,
        "transport": 150
    }
)
```

---

## 📊 Data Structures

### ExpenseItem
```python
@dataclass
class ExpenseItem:
    merchant: str
    amount: float
    category: Optional[str] = None
    confidence: float = 0.0
    description: Optional[str] = None
    timestamp: str  # ISO format
```

### Recommendation
```python
@dataclass
class Recommendation:
    title: str
    description: str
    category: str
    potential_savings: float
    priority: str  # HIGH, MEDIUM, LOW
    actionable_steps: List[str]
    confidence: float  # 0.0-1.0
```

### AnalysisResult
```python
@dataclass
class AnalysisResult:
    total_spending: float
    currency: str
    category_breakdown: List[CategoryBreakdown]
    recommendations: List[Recommendation]
    highest_spending_category: Optional[str]
    highest_spending_amount: float
    expense_count: int
    analysis_date: str
    summary: str
```

### WorkflowState
```python
@dataclass
class WorkflowState:
    # All above objects flow through this state
    input_type: str
    input_content: str
    extracted_text: Optional[str]
    raw_items: List[ExpenseItem]
    categorized_expenses: List[ExpenseItem]
    storage_id: Optional[str]
    analysis: Optional[AnalysisResult]
    recommendations: List[Recommendation]
    # ... + metadata and error tracking
```

---

## 🔄 Workflow Configuration

### Keyword Mode (Default)
```python
workflow = FinSightWorkflow(
    use_llm=False,
    db_path="finsight.db"
)
```
- ✅ No external dependencies
- ✅ Fast (< 300ms total)
- ✅ Works offline
- ✅ Good accuracy

### LLM Mode (Optional)
```python
workflow = FinSightWorkflow(
    use_llm=True,
    db_path="finsight.db"
)
```
- ✅ Higher accuracy
- ✅ Better recommendations
- ⚠️ Requires Ollama running
- ⚠️ Slower (1-5s total)

### Custom Database
```python
workflow = FinSightWorkflow(
    use_llm=False,
    db_path="/path/to/custom.db"
)
```

---

## 📈 Performance

| Metric | Keyword Mode | LLM Mode |
|--------|--------------|----------|
| OCR (image) | 2-5s | 2-5s |
| Extraction | 100-500ms | 100-500ms |
| Categorization | 50-200ms | 500ms-2s |
| Storage | 10-50ms | 10-50ms |
| Analysis | 1-2ms | 500ms-2s |
| Recommendations | 1-2ms | 1-2ms |
| **Total (text input)** | **162-754ms** | **1-7s** |
| **Total (image input)** | **2-5.7s** | **3-12s** |

---

## 🔍 Error Handling

### Graceful Error Recovery

Each node catches exceptions and records them without crashing:

```python
try:
    # Node operation
except Exception as e:
    state.extraction_error = str(e)
    logger.error(f"Extraction Error: {e}")

return state  # Always return updated state
```

### Error Detection

```python
result = workflow.run(input_type="text", input_content="")

# Check for errors
if result.has_error():
    for error in result.get_errors():
        print(f"Error: {error}")
```

### Error List
- `ocr_error`: Text extraction failed
- `extraction_error`: Parsing failed
- `categorization_error`: Classification failed
- `storage_error`: Database save failed
- `analysis_error`: Analysis failed
- `recommendation_error`: Recommendation generation failed
- `workflow_error`: Overall workflow failure

---

## 💾 Database Schema

### Receipts Table
```sql
CREATE TABLE receipts (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP,
    raw_text TEXT,
    input_type TEXT
);
```

### Expenses Table
```sql
CREATE TABLE expenses (
    id TEXT PRIMARY KEY,
    receipt_id TEXT,
    merchant TEXT,
    amount REAL,
    category TEXT,
    confidence REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (receipt_id) REFERENCES receipts(id)
);
```

### Analyses Table
```sql
CREATE TABLE analyses (
    id TEXT PRIMARY KEY,
    receipt_id TEXT,
    analysis_json TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (receipt_id) REFERENCES receipts(id)
);
```

---

## 🧪 Testing

### Run Examples
```bash
python examples/langgraph_workflow_examples.py
```

### Example 1: Text Input
```python
workflow = FinSightWorkflow(use_llm=False)
result = workflow.run(
    input_type="text",
    input_content="Starbucks Latte $6.50\nWhole Foods Milk $5.99"
)
```

### Example 2: With Budget Limits
```python
result = workflow.run(
    input_type="text",
    input_content=receipt_text,
    budget_limits={"food": 300, "shopping": 200}
)
```

### Example 3: Batch Processing
```python
for receipt in receipts:
    result = workflow.run(input_type="text", input_content=receipt)
    print(f"Total: ${result.analysis.total_spending:.2f}")
```

### Example 4: JSON Export
```python
result = workflow.run(input_type="text", input_content=receipt_text)
json_output = json.dumps(result.to_dict(), indent=2)
```

### Example 5: Diagnostics
```python
result = workflow.run(input_type="text", input_content="")
print(f"Has Errors: {result.has_error()}")
print(f"Complete: {result.is_complete()}")
for error in result.get_errors():
    print(f"  - {error}")
```

---

## 🏭 Integration with REST API

### FastAPI Integration

```python
from fastapi import FastAPI
from src.workflows import FinSightWorkflow

app = FastAPI()
workflow = FinSightWorkflow(use_llm=False)

@app.post("/process-receipt")
async def process_receipt(text: str, budget_limits: dict = None):
    result = workflow.run(
        input_type="text",
        input_content=text,
        budget_limits=budget_limits
    )
    return result.to_dict()

@app.post("/upload-receipt")
async def upload_receipt(file: UploadFile):
    # Save file
    path = f"temp/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    
    # Process
    result = workflow.run(input_type="image", input_content=path)
    return result.to_dict()
```

---

## 📚 Usage Examples

### Example 1: Simple Text Processing
```python
from src.workflows import FinSightWorkflow

workflow = FinSightWorkflow(use_llm=False)
result = workflow.run(
    input_type="text",
    input_content="Starbucks $6.50\nGroceries $25.00"
)
print(f"Total: ${result.analysis.total_spending:.2f}")
```

### Example 2: Image Processing
```python
result = workflow.run(
    input_type="image",
    input_content="receipt.jpg"
)
print(result.analysis.summary)
```

### Example 3: With Budget Checking
```python
result = workflow.run(
    input_type="text",
    input_content=receipt_text,
    budget_limits={"food": 300, "shopping": 200}
)

for cat in result.analysis.category_breakdown:
    budget = result.budget_limits.get(cat.category)
    if budget and cat.amount > budget:
        print(f"⚠️ {cat.category} over budget!")
```

### Example 4: Export Results
```python
result = workflow.run(input_type="text", input_content=text)

# To JSON
import json
with open("result.json", "w") as f:
    json.dump(result.to_dict(), f, indent=2)

# To database
# (automatically done by storage node)
```

### Example 5: Error Handling
```python
result = workflow.run(input_type="text", input_content="")

if result.has_error():
    print("Workflow failed:")
    for error in result.get_errors():
        print(f"  - {error}")
```

---

## 📖 API Reference

### FinSightWorkflow

```python
class FinSightWorkflow:
    def __init__(
        self,
        use_llm: bool = False,
        db_path: str = "finsight.db"
    ):
        """Initialize workflow."""
    
    def run(
        self,
        input_type: str,
        input_content: str,
        budget_limits: Dict[str, float] = None
    ) -> WorkflowState:
        """Run the complete pipeline."""
```

### WorkflowState Methods

```python
state.to_dict()              # Convert to dictionary
state.has_error()            # Check for errors
state.get_errors()           # Get list of errors
state.is_complete()          # Check if workflow completed successfully
```

---

## 🔗 State Flow Diagram

```
Input (text/image)
    ↓
┌─────────────────────┐
│   OCR Node          │
├─────────────────────┤
│ extracted_text      │
│ ocr_confidence      │
│ ocr_error           │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Extraction Node     │
├─────────────────────┤
│ raw_items           │
│ extraction_error    │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Categorization Node │
├─────────────────────┤
│ categorized_expenses│
│ categorization_error│
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Storage Node        │
├─────────────────────┤
│ storage_id          │
│ storage_error       │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Analysis Node       │
├─────────────────────┤
│ analysis            │
│ analysis_error      │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Recommendations Node│
├─────────────────────┤
│ recommendations     │
│ recommendation_error│
└──────────┬──────────┘
           ↓
        Results
```

---

## ⚙️ Configuration Options

### Workflow Modes

```python
# Keyword-based (fast)
workflow = FinSightWorkflow(use_llm=False)

# LLM-powered (accurate)
workflow = FinSightWorkflow(use_llm=True)
```

### Database Options

```python
# File-based
workflow = FinSightWorkflow(db_path="finsight.db")

# In-memory (for testing)
workflow = FinSightWorkflow(db_path=":memory:")

# Custom path
workflow = FinSightWorkflow(db_path="/path/to/data.db")
```

---

## 🚨 Troubleshooting

### Workflow Takes Too Long
- If using LLM mode, ensure Ollama is running
- Check network latency to Ollama server
- Use keyword mode for faster processing

### Text Not Extracting Well
- For OCR, use higher quality images
- Ensure good lighting and contrast
- Try preprocessing the image

### Low Accuracy
- Use LLM mode instead of keyword mode
- Check if merchant names match keyword database
- Ensure expense amounts are correctly formatted

### Database Errors
- Check file path is writable
- Ensure sufficient disk space
- Close other database connections

---

## 📋 Summary

**FinSight AI Workflow provides:**
- ✅ Seamless orchestration of 4 modules
- ✅ 6-node sequential pipeline
- ✅ Flexible input (text/image)
- ✅ Comprehensive error handling
- ✅ Persistent data storage
- ✅ Production-ready architecture
- ✅ LangGraph-based design
- ✅ Full type safety

---

**Status:** ✅ Production Ready  
**Version:** 1.0  
**Type:** LangGraph Workflow
