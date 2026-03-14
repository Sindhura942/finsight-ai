"""Architecture Overview - FinSight AI"""

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                         │
│  - Receipt Upload                                               │
│  - Dashboard & Analytics                                        │
│  - Expense Management                                           │
│  - Recommendations Display                                      │
└────────────────┬────────────────────────────────────────────────┘
                 │ HTTP/REST
┌────────────────▼────────────────────────────────────────────────┐
│              FastAPI Backend Server                              │
├─────────────────────────────────────────────────────────────────┤
│ API Routes                                                       │
│  - /api/expenses (CRUD operations)                              │
│  - /api/insights (Analytics)                                    │
│  - /api/health (Health checks)                                  │
├─────────────────────────────────────────────────────────────────┤
│ Service Layer                                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ ExpenseService        │ InsightService   │ OCRService     │  │
│  │ - Process receipts    │ - Spending data  │ - Extract text │  │
│  │ - CRUD operations     │ - Analytics      │ - Confidence   │  │
│  │ - Orchestration       │ - Trends         │ - Preprocess   │  │
│  └──────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│ LLM & Workflow Layer                                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ LLMService              │ LangGraph Workflows             │  │
│  │ - Extract details       │ - Receipt processing pipeline   │  │
│  │ - Categorization        │ - Error handling                │  │
│  │ - Recommendations       │ - State management              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────────┘
                 │
        ┌────────┴─────────┬──────────────┐
        │                  │              │
┌───────▼────────┐ ┌──────▼──────┐ ┌────▼───────┐
│  SQLite DB     │ │   Ollama    │ │  Tesseract │
│  (Expenses)    │ │  (Llama3)   │ │  (OCR)     │
└────────────────┘ └─────────────┘ └────────────┘
```

## Key Components

### 1. Frontend (Streamlit)
- **Location:** `frontend/app.py`
- **Responsibilities:**
  - User interface for expense management
  - Receipt image upload
  - Dashboard and analytics visualization
  - Cost-saving recommendations display
- **Dependencies:** requests, streamlit, plotly, pandas

### 2. Backend API (FastAPI)
- **Location:** `backend/main.py`
- **Features:**
  - RESTful API for all operations
  - CORS support for frontend communication
  - Automatic API documentation
  - Health checks and monitoring

### 3. Service Layer
- **OCRService** (`app/services/ocr_service.py`)
  - Extracts text from receipt images using Tesseract
  - Calculates OCR confidence scores
  - Image preprocessing and optimization

- **LLMService** (`app/services/llm_service.py`)
  - Communicates with Ollama/Llama3
  - Extracts merchant details from text
  - Categorizes expenses automatically
  - Generates cost-saving recommendations

- **ExpenseService** (`app/services/expense_service.py`)
  - Orchestrates receipt processing workflow
  - Manages CRUD operations
  - Integrates OCR and LLM services

- **InsightService** (`app/services/insight_service.py`)
  - Generates spending summaries
  - Analyzes spending trends
  - Creates recommendations

### 4. Database Layer
- **SQLite Database** (`finsight.db`)
  - Stores all expenses
  - Indexed queries for performance
  - Repository pattern for data access

- **Models:**
  - `ExpenseORM`: Database model for expenses
  - `ExpenseRepository`: Data access object

### 5. Workflows (LangGraph)
- **Location:** `app/workflows/`
- **Receipt Processing Workflow:**
  1. Extract text from image (OCR)
  2. Parse merchant and amount (LLM)
  3. Categorize expense (LLM)
  4. Store in database
  5. Error handling and recovery

## Data Flow

```
User Upload Receipt
    ↓
Receipt Image → [Streamlit Frontend]
    ↓
Upload to Backend [FastAPI]
    ↓
OCRService extracts text
    ↓
LLMService extracts/categorizes
    ↓
ExpenseService creates record
    ↓
SQLite Database stores
    ↓
Return ExpenseResponse
    ↓
Frontend displays result
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Web UI |
| API | FastAPI | REST API |
| Orchestration | LangGraph | Workflow management |
| LLM | Ollama + Llama3 | AI/ML operations |
| OCR | Tesseract | Image text extraction |
| Database | SQLite + SQLAlchemy | Data persistence |
| Validation | Pydantic | Data validation |
| Testing | pytest | Unit tests |

## Module Organization

```
backend/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── expenses.py
│   │   ├── insights.py
│   │   └── health.py
│   ├── core/
│   │   ├── config.py          # Settings management
│   │   ├── constants.py       # App constants
│   │   └── logger.py          # Logging setup
│   ├── models/
│   │   ├── expense.py         # Expense schemas
│   │   └── insights.py        # Insight schemas
│   ├── services/
│   │   ├── ocr_service.py
│   │   ├── llm_service.py
│   │   ├── expense_service.py
│   │   └── insight_service.py
│   ├── workflows/
│   │   └── receipt_workflow.py
│   └── database/
│       ├── session.py         # DB connection
│       ├── models.py          # ORM models
│       └── repository.py      # Data access
├── tests/
├── main.py                    # FastAPI app
└── requirements.txt

frontend/
├── app.py                     # Streamlit app
└── pages/                     # Multi-page sections
```

## API Endpoints

### Expenses
- `POST /api/expenses/upload` - Process receipt image
- `POST /api/expenses/` - Create expense
- `GET /api/expenses/` - List expenses
- `GET /api/expenses/{id}` - Get expense details
- `PUT /api/expenses/{id}` - Update expense
- `DELETE /api/expenses/{id}` - Delete expense

### Insights
- `GET /api/insights/spending-summary` - Get summary
- `GET /api/insights/by-category` - Category breakdown
- `GET /api/insights/trends` - Spending trends
- `POST /api/insights/recommendations` - Get suggestions

### Health
- `GET /api/health/` - Check system health

## Configuration

Environment variables in `.env`:
- `API_HOST`, `API_PORT` - Server configuration
- `OLLAMA_BASE_URL`, `OLLAMA_MODEL` - LLM settings
- `DATABASE_URL` - SQLite path
- `TESSERACT_PATH` - OCR executable path
- `LOG_LEVEL` - Logging verbosity

## Performance Considerations

1. **Database Indexing:** Expenses indexed by category, date, and user
2. **Caching:** Consider Redis for frequently accessed insights
3. **Async Operations:** FastAPI uses async for I/O operations
4. **OCR Optimization:** Image preprocessing improves accuracy
5. **LLM Caching:** Cache categorizations for common merchants

## Security Considerations

1. **Input Validation:** Pydantic models validate all inputs
2. **File Upload:** Size limits and extension validation
3. **API Rate Limiting:** Consider adding rate limiting middleware
4. **CORS:** Configured for frontend domain
5. **Database:** SQLite suitable for single-user; upgrade for multi-user
