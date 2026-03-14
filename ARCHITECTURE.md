"""Project structure and architecture documentation"""

# FinSight AI - Clean Project Structure

## Overview

FinSight AI is an intelligent financial expense tracking and cost-saving recommendation system built with modern Python web technologies. The application uses:

- **OCR (Optical Character Recognition)**: Tesseract for receipt image processing
- **LLM (Large Language Model)**: Ollama with Llama3 for natural language understanding
- **Backend API**: FastAPI for REST endpoints
- **Database**: SQLAlchemy ORM with SQLite
- **Workflow Orchestration**: LangGraph for multi-step receipt processing

## Project Structure

```
FinSight AI/
├── src/                          # Main source code package
│   ├── __init__.py
│   ├── config/                   # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py           # Pydantic BaseSettings for environment config
│   │
│   ├── schemas/                  # Pydantic models for API validation
│   │   └── __init__.py           # ExpenseResponse, SpendingSummary, etc.
│   │
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py             # get_logger() with loguru integration
│   │   ├── validators.py         # File/image validation functions
│   │   └── helpers.py            # Text formatting, date parsing, etc.
│   │
│   ├── prompts/                  # LLM prompt templates
│   │   └── __init__.py           # 8 prompt templates + registry
│   │
│   ├── database/                 # Database layer
│   │   ├── __init__.py
│   │   ├── session.py            # SQLAlchemy setup and session management
│   │   ├── models.py             # ORM models (Expense table)
│   │   └── repository.py         # ExpenseRepository with CRUD + queries
│   │
│   ├── ocr/                      # Receipt OCR processing
│   │   ├── __init__.py
│   │   └── processor.py          # OCRProcessor class for Tesseract
│   │
│   ├── agents/                   # AI agents for LLM operations
│   │   ├── __init__.py
│   │   ├── llm_agent.py          # Base LLMAgent class
│   │   ├── categorizer.py        # CategorizerAgent for expense classification
│   │   ├── analyzer.py           # AnalyzerAgent for spending analysis
│   │   └── recommender.py        # RecommenderAgent for suggestions
│   │
│   ├── services/                 # Business logic orchestration
│   │   ├── __init__.py
│   │   ├── receipt_service.py    # Process receipts, extract data
│   │   ├── expense_service.py    # Manage expenses (CRUD)
│   │   └── insight_service.py    # Generate insights and recommendations
│   │
│   └── api/                      # REST API endpoints
│       ├── __init__.py
│       ├── expenses.py           # /api/expenses/* endpoints
│       ├── insights.py           # /api/insights/* endpoints
│       └── health.py             # /api/health/* endpoints
│
├── main.py                       # FastAPI application entry point
├── langgraph_flow.py            # LangGraph workflow for receipt processing
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file

```

## Architecture Patterns

### 1. **Agent Architecture**
The application uses specialized AI agents for different LLM tasks:
- **LLMAgent**: Base class for all LLM operations
- **CategorizerAgent**: Classifies expenses into categories
- **AnalyzerAgent**: Analyzes spending patterns and detects anomalies
- **RecommenderAgent**: Generates cost-saving suggestions

### 2. **Repository Pattern**
Database access is abstracted through repositories:
- **ExpenseRepository**: Encapsulates all Expense queries
- Methods: create(), get_by_id(), get_by_category(), get_spending_by_category(), etc.

### 3. **Service Layer**
Business logic is organized in services that orchestrate agents and repositories:
- **ReceiptService**: Coordinates OCR, LLM, and categorization
- **ExpenseService**: Manages expense CRUD operations
- **InsightService**: Generates analytics and recommendations

### 4. **Dependency Injection (FastAPI)**
- Services receive dependencies via constructor
- Database sessions are managed by FastAPI dependencies
- Clean separation of concerns

### 5. **Prompt Management**
- Centralized prompt templates in `/src/prompts/`
- Registry pattern for prompt lookup
- Format function for variable substitution

## Module Details

### Config Module (`src/config/`)
Manages application settings using Pydantic BaseSettings:
```python
from src.config import get_settings

settings = get_settings()  # Cached settings from environment
```

**Key Settings:**
- `DATABASE_URL`: SQLite database path
- `OLLAMA_BASE_URL`: LLM service endpoint
- `CORS_ORIGINS`: Allowed CORS origins
- `MAX_UPLOAD_SIZE`: File upload limit
- `LOG_LEVEL`: Application logging level

### Schemas Module (`src/schemas/`)
Pydantic models for API validation and type safety:
```python
ExpenseCreate, ExpenseUpdate, ExpenseResponse
SpendingSummary, CategoryInsight, RecommendationsResponse
ReceiptData, ReceiptProcessingResult
```

### Utils Module (`src/utils/`)
Reusable utility functions:
```python
get_logger(name)  # Structured logging with loguru
validate_image_file(path)  # Validate image files
format_currency(amount)  # Format money
parse_date(date_string)  # Parse dates
```

### Database Module (`src/database/`)
SQLAlchemy ORM setup and data access:
```python
# ORM Model
class Expense(Base):
    id, merchant_name, amount, category, date, etc.

# Repository
repository = ExpenseRepository(db)
expenses = repository.get_by_category("food")
total = repository.get_total_spending(start_date, end_date)
```

### OCR Module (`src/ocr/`)
Receipt text extraction using Tesseract:
```python
from src.ocr import OCRProcessor

ocr = OCRProcessor()
text, confidence = ocr.extract_from_image("receipt.png")
```

### Agents Module (`src/agents/`)
AI agents for LLM operations:
```python
# Categorize
categorizer = CategorizerAgent()
category = categorizer.categorize("Target Store")

# Analyze
analyzer = AnalyzerAgent()
insights = analyzer.analyze_spending(spending_data)

# Recommend
recommender = RecommenderAgent()
suggestions = recommender.generate_recommendations(text)
```

### Services Module (`src/services/`)
Business logic orchestration:
```python
# Process receipt
receipt_service = ReceiptService(db)
result = receipt_service.process_receipt("receipt.png")

# Manage expenses
expense_service = ExpenseService(db)
expense = expense_service.create(expense_data)

# Get insights
insight_service = InsightService(db)
summary = insight_service.get_spending_summary(days=30)
```

### API Module (`src/api/`)
FastAPI REST endpoints organized by resource:

**Expenses** (`/api/expenses/`):
- `POST /` - Create new expense
- `GET /{id}` - Get expense by ID
- `GET /` - List all expenses
- `PUT /{id}` - Update expense
- `DELETE /{id}` - Delete expense
- `POST /upload-receipt/` - Process receipt image

**Insights** (`/api/insights/`):
- `GET /summary` - Spending summary
- `GET /recommendations` - Cost-saving recommendations
- `GET /trends` - Spending trends

**Health** (`/api/health/`):
- `GET /` - Basic health check
- `GET /database` - Database health
- `GET /llm` - LLM service health
- `GET /status` - Full system status

## LangGraph Workflow

`langgraph_flow.py` implements receipt processing using LangGraph:

```
[Start] → extract_text_node → parse_details_node → categorize_node 
          → create_expense_node → [End]
```

**State Structure:**
```python
ReceiptProcessingState:
  - image_path: str
  - extracted_text: str
  - ocr_confidence: float
  - merchant_name: str
  - amount: float
  - category: str
  - expense_data: Optional[ExpenseCreate]
  - error: Optional[str]
```

## Running the Application

### Prerequisites
1. Python 3.9+
2. Tesseract OCR installed
3. Ollama running locally with Llama3 model

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the application
python main.py
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Usage Examples

**Upload and process receipt:**
```bash
curl -X POST "http://localhost:8000/api/expenses/upload-receipt/" \
  -F "file=@receipt.png"
```

**Get spending summary:**
```bash
curl "http://localhost:8000/api/insights/summary?days=30"
```

**Get recommendations:**
```bash
curl "http://localhost:8000/api/insights/recommendations?days=30"
```

## Design Decisions

### Why This Structure?

1. **`src/` Package**: Cleaner than nested `backend/app/` structure. Single source package.

2. **Separated Concerns**: Each module has a single responsibility:
   - Config: Settings management
   - Database: Data persistence
   - OCR: Image text extraction
   - Agents: LLM operations
   - Services: Business logic
   - API: REST endpoints

3. **Agent Architecture**: LLM operations are encapsulated in specialized agent classes:
   - Reusable across services
   - Easy to test independently
   - Clear separation of AI logic

4. **Prompt Management**: Centralized prompts enable:
   - Easy version control of prompts
   - Registry pattern for lookup
   - Consistent LLM interactions

5. **Repository Pattern**: Database operations are isolated:
   - Change database without changing services
   - Rich query methods for common operations
   - Easy testing with mock repositories

6. **Service Layer**: Acts as orchestrator:
   - Coordinates agents, repositories, and schemas
   - Handles cross-cutting concerns
   - Business logic separated from API handlers

7. **LangGraph Workflow**: Multi-step receipt processing:
   - Clear state transitions
   - Error handling at each step
   - Easy to extend with new steps

## Testing

Create a `tests/` directory with:
- `test_ocr.py` - Test OCR processor
- `test_agents.py` - Test AI agents
- `test_services.py` - Test business logic
- `test_api.py` - Test endpoints

## Next Steps

1. **Configuration**: Update `.env.example` with actual values
2. **Database**: Create SQLite database or connect to PostgreSQL
3. **LLM Setup**: Ensure Ollama is running with Llama3
4. **Testing**: Implement unit and integration tests
5. **Frontend**: Create Streamlit dashboard in separate directory
6. **Documentation**: Add API documentation and deployment guides

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point |
| `langgraph_flow.py` | Receipt processing workflow |
| `requirements.txt` | Project dependencies |
| `src/config/settings.py` | Application settings |
| `src/database/models.py` | ORM models |
| `src/agents/llm_agent.py` | Base AI agent class |
| `src/api/expenses.py` | Expense endpoints |
| `src/services/receipt_service.py` | Receipt processing logic |

## Technologies

- **Framework**: FastAPI (modern, fast Python web framework)
- **Database**: SQLAlchemy + SQLite (ORM with SQL flexibility)
- **LLM**: Ollama + Llama3 (local LLM, no external API)
- **OCR**: Tesseract (open-source text extraction)
- **Validation**: Pydantic (runtime type checking)
- **Logging**: loguru (modern Python logging)
- **Workflow**: LangGraph (multi-step AI workflows)

## Summary

This clean project structure emphasizes:
- **Modularity**: Clear separation of concerns
- **Reusability**: Shared utilities and base classes
- **Testability**: Isolated components with clear interfaces
- **Scalability**: Easy to add new agents, services, and endpoints
- **Maintainability**: Organized code with consistent patterns
