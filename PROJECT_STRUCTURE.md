"""Visual overview and getting started guide"""

# FinSight AI - Complete Project Structure

## 📁 Directory Structure

```
/Users/sindhuram/Downloads/FinSight AI/
│
├── src/                          ⭐ Main application package
│   ├── config/                   🔧 Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           Pydantic BaseSettings
│   │
│   ├── schemas/                  📋 Pydantic validation models
│   │   └── __init__.py           11 data models
│   │
│   ├── utils/                    🛠️  Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py             Loguru integration
│   │   ├── validators.py         File/image validation
│   │   └── helpers.py            Text/date utilities
│   │
│   ├── prompts/                  💬 LLM prompt templates
│   │   └── __init__.py           8 prompts + registry
│   │
│   ├── database/                 🗄️  Data persistence layer
│   │   ├── __init__.py
│   │   ├── session.py            SQLAlchemy setup
│   │   ├── models.py             ORM models (Expense)
│   │   └── repository.py         Data access pattern
│   │
│   ├── ocr/                      📸 Text extraction
│   │   ├── __init__.py
│   │   └── processor.py          Tesseract wrapper
│   │
│   ├── agents/                   🤖 AI agents for LLM
│   │   ├── __init__.py
│   │   ├── llm_agent.py          Base agent class
│   │   ├── categorizer.py        Classification agent
│   │   ├── analyzer.py           Analysis agent
│   │   └── recommender.py        Suggestion agent
│   │
│   ├── services/                 ⚙️  Business logic layer
│   │   ├── __init__.py
│   │   ├── receipt_service.py    Process receipts
│   │   ├── expense_service.py    Manage expenses
│   │   └── insight_service.py    Generate analytics
│   │
│   └── api/                      🔌 REST API endpoints
│       ├── __init__.py
│       ├── expenses.py           Expense routes
│       ├── insights.py           Analytics routes
│       └── health.py             Health check routes
│
├── main.py                       ⚡ FastAPI application
├── langgraph_flow.py            🔄 Receipt processing workflow
├── requirements.txt             📦 Dependencies
├── .env.example                 ⚙️  Configuration template
│
└── Documentation/
    ├── ARCHITECTURE.md           Complete guide
    ├── QUICK_REFERENCE.md       Quick tips
    ├── RESTRUCTURING_COMPLETE.md Summary
    ├── README.md                 Getting started
    └── Other docs...
```

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
cd "/Users/sindhuram/Downloads/FinSight AI"
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings (optional - defaults work)
```

### Step 3: Ensure Ollama is Running
```bash
# In a separate terminal
ollama serve

# In another terminal (one-time setup)
ollama pull llama3
```

### Step 4: Run the Application
```bash
python main.py
```

### Step 5: Try It Out!
```
Open browser: http://localhost:8000/docs
Try the interactive API documentation
```

## 📚 Module Overview

### 1️⃣  Configuration (`src/config/`)
Manages all application settings using Pydantic:
- Database connection string
- LLM service URL
- CORS settings
- File upload limits
- Logging levels

```python
from src.config import get_settings
settings = get_settings()  # Cached settings object
```

### 2️⃣  Schemas (`src/schemas/`)
Pydantic models for type-safe API validation:
- `ExpenseCreate` - Request data for new expense
- `ExpenseResponse` - Response data for expense
- `SpendingSummary` - Analytics summary
- `RecommendationsResponse` - AI suggestions
- And 6 more...

### 3️⃣  Utilities (`src/utils/`)
Reusable functions across application:

**Logging:**
```python
from src.utils import get_logger
logger = get_logger("module_name")
logger.info("Something happened")
```

**Validation:**
```python
from src.utils import validate_image_file
validate_image_file("/path/to/image.png")
```

**Formatting:**
```python
from src.utils import format_currency, parse_date
price = format_currency(99.99)  # "$99.99"
date = parse_date("2024-01-15")
```

### 4️⃣  Prompts (`src/prompts/`)
Centralized LLM prompt management:
- `extract_merchant` - Extract merchant name from text
- `extract_amount` - Extract amount from text
- `categorize_expense` - Classify expense category
- `analyze_spending` - Analyze spending patterns
- `generate_recommendations` - Generate suggestions
- And 3 more...

```python
from src.prompts import get_prompt, format_prompt
prompt = get_prompt("categorize_expense")
filled = format_prompt(prompt, text="Target Store")
```

### 5️⃣  Database (`src/database/`)
SQLAlchemy ORM with repository pattern:

```python
from src.database import SessionLocal
from src.database.repository import ExpenseRepository

db = SessionLocal()
repo = ExpenseRepository(db)

# Create
expense = repo.create(expense_data)

# Read
expenses = repo.get_by_category("food")

# Update
repo.update(expense_id, updated_data)

# Delete
repo.delete(expense_id)

# Analytics
total = repo.get_total_spending(start, end)
by_category = repo.get_spending_by_category(start, end)
```

### 6️⃣  OCR (`src/ocr/`)
Receipt image text extraction:

```python
from src.ocr import OCRProcessor

ocr = OCRProcessor()
text, confidence = ocr.extract_from_image("receipt.png")
# confidence is 0.0-1.0, where 1.0 is perfect
```

### 7️⃣  Agents (`src/agents/`)
AI agents for LLM operations:

```python
from src.agents import CategorizerAgent, AnalyzerAgent, RecommenderAgent

# Categorize
cat = CategorizerAgent()
category = cat.categorize("Target Store")  # Returns "shopping"

# Analyze
analyzer = AnalyzerAgent()
insights = analyzer.analyze_spending(spending_data)

# Recommend
rec = RecommenderAgent()
suggestions = rec.generate_recommendations(analysis_text)
```

### 8️⃣  Services (`src/services/`)
Business logic orchestrating agents and repositories:

```python
from src.services import ReceiptService, ExpenseService, InsightService
from src.database import SessionLocal

db = SessionLocal()

# Process receipt
receipt_svc = ReceiptService(db)
result = receipt_svc.process_receipt("receipt.png")

# Manage expenses
expense_svc = ExpenseService(db)
expense = expense_svc.create(expense_data)
all_expenses = expense_svc.get_all(skip=0, limit=100)

# Get insights
insight_svc = InsightService(db)
summary = insight_svc.get_spending_summary(days=30)
recommendations = insight_svc.get_recommendations(days=30)
```

### 9️⃣  API (`src/api/`)
REST endpoints organized by resource:

**Expense Endpoints:**
- `POST /api/expenses/` - Create expense
- `GET /api/expenses/{id}` - Get by ID
- `GET /api/expenses/` - List all
- `PUT /api/expenses/{id}` - Update
- `DELETE /api/expenses/{id}` - Delete
- `POST /api/expenses/upload-receipt/` - Process receipt

**Insight Endpoints:**
- `GET /api/insights/summary` - Summary by category
- `GET /api/insights/recommendations` - Suggestions
- `GET /api/insights/trends` - Trend analysis

**Health Endpoints:**
- `GET /api/health/` - Basic check
- `GET /api/health/database` - DB check
- `GET /api/health/llm` - LLM check
- `GET /api/health/status` - Full status

## 🔄 Receipt Processing Workflow

The `langgraph_flow.py` implements multi-step receipt processing:

```
┌──────────────┐
│   Upload     │
│   Receipt    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  OCR Extraction      │
│  (Tesseract)         │
│  Returns: text, conf │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Parse Details       │
│  (LLM)               │
│  Extract: merchant   │
│          amount      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Categorize          │
│  (LLM Agent)         │
│  Returns: category   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Save to DB          │
│  (Repository)        │
│  Returns: expense_id │
└──────┬───────────────┘
       │
       ▼
┌──────────────┐
│   Return     │
│   Result     │
└──────────────┘
```

## 🧪 Testing the API

### Using curl
```bash
# Health check
curl http://localhost:8000/api/health/status

# Create expense
curl -X POST http://localhost:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_name": "Target",
    "amount": 25.50,
    "category": "shopping"
  }'

# Get summary
curl "http://localhost:8000/api/insights/summary?days=30"

# Upload receipt
curl -X POST http://localhost:8000/api/expenses/upload-receipt/ \
  -F "file=@receipt.png"
```

### Using Interactive Docs
1. Open http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Enter parameters
5. Click "Execute"

## 📝 Example Code Snippets

### Create an Expense Programmatically
```python
from src.database import SessionLocal
from src.services import ExpenseService
from src.schemas import ExpenseCreate
from datetime import datetime

db = SessionLocal()
service = ExpenseService(db)

expense_data = ExpenseCreate(
    merchant_name="Starbucks",
    amount=5.95,
    category="food & drinks",
    description="Morning coffee"
)

expense = service.create(expense_data)
print(f"Created expense: {expense.id}")
```

### Analyze Spending
```python
from src.database import SessionLocal
from src.services import InsightService

db = SessionLocal()
service = InsightService(db)

summary = service.get_spending_summary(days=30)
print(f"Total spending: ${summary.total_spending:.2f}")
print(f"Transactions: {summary.transaction_count}")
print(f"Highest category: {summary.highest_category}")

for category in summary.categories:
    print(f"  {category.category}: ${category.total_amount:.2f}")
```

### Get Recommendations
```python
from src.database import SessionLocal
from src.services import InsightService

db = SessionLocal()
service = InsightService(db)

recommendations = service.get_recommendations(days=30)
print(f"Potential savings: ${recommendations.total_potential_savings:.2f}")
for suggestion in recommendations.suggestions:
    print(f"  - {suggestion}")
```

## ⚙️  Configuration (.env)

Key environment variables:

```
# Database
DATABASE_URL=sqlite:///./finsight.db

# LLM Service
OLLAMA_BASE_URL=http://localhost:11434

# API
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8501"]

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
```

## 🎯 Common Tasks

### Add a New API Endpoint
1. Create handler function in `src/api/`
2. Use `@router.get()`, `@router.post()`, etc.
3. Accept `Session = Depends(get_db)` for database
4. Return Pydantic schema for response
5. Endpoint automatically added to `/docs`

### Add a New AI Agent
1. Create class in `src/agents/` inheriting from `LLMAgent`
2. Implement custom methods using `self.generate()`
3. Use prompts from `src/prompts/`
4. Import and use in services

### Add a New Prompt
1. Add to `PROMPTS` dict in `src/prompts/__init__.py`
2. Use `PromptTemplate` dataclass
3. Access with `get_prompt(name)`
4. Format with `format_prompt(template, **kwargs)`

### Query Database
1. Create `ExpenseRepository(db)` instance
2. Use methods: `get_by_category()`, `get_total_spending()`, etc.
3. Or write custom queries with SQLAlchemy

## 📊 Monitoring & Debugging

### Check System Status
```bash
curl http://localhost:8000/api/health/status
```

Returns:
```json
{
  "overall": "healthy",
  "components": {
    "database": "healthy",
    "llm": "healthy"
  }
}
```

### View Logs
```bash
# Logs are written to console and file
# File location defined in settings
tail -f logs/finsight.log
```

### Debug with REPL
```python
from src.database import SessionLocal
from src.database.repository import ExpenseRepository

db = SessionLocal()
repo = ExpenseRepository(db)

# List all expenses
for exp in repo.get_all():
    print(exp)
```

## 🔐 Production Considerations

1. **Database**: Switch from SQLite to PostgreSQL
2. **Secrets**: Use environment variables for sensitive data
3. **CORS**: Configure allowed origins properly
4. **Authentication**: Add JWT token validation
5. **Rate Limiting**: Add request rate limiting
6. **Monitoring**: Set up log aggregation
7. **Backup**: Schedule database backups
8. **SSL/TLS**: Use HTTPS in production

## 📖 Documentation Files

- **ARCHITECTURE.md** - Complete architecture guide
- **QUICK_REFERENCE.md** - Quick reference for developers
- **RESTRUCTURING_COMPLETE.md** - Project completion summary
- **README.md** - Getting started guide
- **main.py** - Inline documentation in code

## 🎓 Learning Path

1. **Start here**: Run the application (`python main.py`)
2. **Try the API**: Visit http://localhost:8000/docs
3. **Explore modules**: Read docstrings in each module
4. **Trace workflow**: Follow receipt processing in `langgraph_flow.py`
5. **Add features**: Create new endpoints and agents
6. **Deploy**: Set up with Docker and cloud platform

## ✅ Verification Checklist

- [x] All 10 src/ subdirectories created
- [x] 30+ Python files created
- [x] FastAPI application (`main.py`)
- [x] LangGraph workflow (`langgraph_flow.py`)
- [x] Requirements file with all dependencies
- [x] Comprehensive documentation
- [x] All modules fully documented with docstrings
- [x] Type hints throughout codebase
- [x] Error handling and logging in place
- [x] Database ORM with repository pattern
- [x] 3 specialized services
- [x] 4 AI agents (base + 3 specialized)
- [x] 8 LLM prompt templates
- [x] 13 REST API endpoints
- [x] Health check endpoints

## 🎉 You're All Set!

The FinSight AI application is ready to use. Start with:

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Run the app
python main.py

# Terminal 3: Try the API
curl http://localhost:8000/api/health/
```

Then visit: **http://localhost:8000/docs**

Happy coding! 🚀
