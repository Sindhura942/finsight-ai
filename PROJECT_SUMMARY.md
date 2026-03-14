"""FinSight AI - Project Summary

A complete, production-quality Python application for AI-powered financial analysis.
"""

## 📋 Project Overview

**FinSight AI** is a sophisticated financial assistant that analyzes user expenses through receipt images and AI, providing actionable spending insights and personalized cost-saving recommendations.

### 🎯 Key Features

1. **Receipt Processing**
   - Upload receipt images (JPG, PNG, etc.)
   - Automatic text extraction using Tesseract OCR
   - Confidence scoring for extraction accuracy

2. **Intelligent Parsing**
   - Extract merchant names and transaction amounts
   - Parse receipt text using Llama3 LLM
   - JSON response formatting

3. **Smart Categorization**
   - Automatic expense categorization using AI
   - 11 predefined expense categories
   - Customizable category system

4. **Expense Management**
   - Create, read, update, delete expenses
   - Manual expense entry
   - Bulk operations support

5. **Financial Analytics**
   - Spending summaries and trends
   - Category-based breakdowns
   - Time-range analysis (1-365 days)
   - Daily spending visualization

6. **AI Recommendations**
   - LLM-powered cost-saving suggestions
   - Priority-ranked recommendations
   - Potential savings calculations
   - Category-specific insights

7. **User Interface**
   - Streamlit web dashboard
   - Multi-page application
   - Interactive charts and visualizations
   - Real-time data updates

## 🏗️ Project Structure

```
FinSight AI/
├── backend/
│   ├── app/
│   │   ├── api/               # FastAPI routes
│   │   │   ├── expenses.py
│   │   │   ├── insights.py
│   │   │   └── health.py
│   │   ├── core/              # Configuration & utilities
│   │   │   ├── config.py
│   │   │   ├── constants.py
│   │   │   └── logger.py
│   │   ├── models/            # Pydantic schemas
│   │   │   ├── expense.py
│   │   │   └── insights.py
│   │   ├── services/          # Business logic
│   │   │   ├── ocr_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── expense_service.py
│   │   │   └── insight_service.py
│   │   ├── workflows/         # LangGraph orchestration
│   │   │   └── receipt_workflow.py
│   │   ├── database/          # Data access layer
│   │   │   ├── session.py
│   │   │   ├── models.py
│   │   │   └── repository.py
│   │   └── __init__.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_repository.py
│   │   └── test_ocr_service.py
│   ├── main.py                # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── app.py                 # Streamlit dashboard
│   └── requirements.txt
├── docs/
│   ├── API.md                 # API documentation
│   ├── SETUP.md               # Installation guide
│   └── ARCHITECTURE.md        # Architecture overview
├── README.md
├── setup.sh / setup.bat       # Quick setup scripts
├── docker-compose.yml
├── .env.example
├── .gitignore
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend Framework** | FastAPI | 0.104.1 |
| **Server** | Uvicorn | 0.24.0 |
| **Frontend** | Streamlit | 1.28.1 |
| **Database** | SQLite + SQLAlchemy | 2.0.23 |
| **LLM Integration** | Ollama + Llama3 | Latest |
| **Workflow** | LangGraph | 0.0.44 |
| **OCR** | Tesseract + pytesseract | 0.3.10 |
| **Validation** | Pydantic | 2.5.0 |
| **Data Processing** | Pandas, NumPy | Latest |
| **Visualization** | Plotly | 5.18.0 |
| **Testing** | pytest | 7.4.3 |
| **Python** | 3.10+ | - |

## 📦 Dependencies

### Backend (36 packages)
- **Core**: FastAPI, Pydantic, Uvicorn
- **Database**: SQLAlchemy, Alembic
- **AI/ML**: LangGraph, Ollama, pytesseract
- **Data**: Pandas, NumPy, Pillow
- **Testing**: pytest, httpx
- **Quality**: Black, Flake8, mypy

### Frontend (5 packages)
- Streamlit
- requests
- Pandas
- Plotly
- NumPy

## 🚀 Getting Started

### Quick Start (macOS)

1. **Clone and navigate:**
   ```bash
   cd ~/Downloads
   git clone <repo-url> "FinSight AI"
   cd "FinSight AI"
   ```

2. **Run setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Start services (3 terminals):**
   ```bash
   # Terminal 1: Ollama
   ollama serve

   # Terminal 2: Backend
   cd backend && source venv/bin/activate && python main.py

   # Terminal 3: Frontend
   cd frontend && source venv/bin/activate && streamlit run app.py
   ```

4. **Access:**
   - API Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8501

### Installation Requirements
- Python 3.10+
- Tesseract OCR
- Ollama + Llama3
- 4GB+ RAM

## 📚 API Endpoints

### Expenses
- `POST /api/expenses/upload` - Process receipt image
- `POST /api/expenses/` - Create expense
- `GET /api/expenses/` - List expenses
- `GET /api/expenses/{id}` - Get details
- `PUT /api/expenses/{id}` - Update
- `DELETE /api/expenses/{id}` - Delete

### Insights
- `GET /api/insights/spending-summary` - Summary
- `GET /api/insights/by-category` - By category
- `GET /api/insights/trends` - Trends
- `POST /api/insights/recommendations` - Recommendations

### Health
- `GET /api/health/` - Health check

## 🎨 Frontend Pages

1. **Dashboard** - Overview and key metrics
2. **Upload Receipt** - Process new receipts
3. **Expenses** - View all expenses
4. **Analytics** - Detailed spending analysis
5. **Recommendations** - Cost-saving suggestions

## 🗄️ Database Schema

**Expenses Table**
- `id` (int, primary key)
- `merchant_name` (varchar, indexed)
- `amount` (float)
- `category` (varchar, indexed)
- `date` (datetime, indexed)
- `description` (text)
- `image_path` (varchar)
- `confidence_score` (float)
- `created_at` (datetime, indexed)
- `updated_at` (datetime)

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ -v --cov=app

# Run specific test file
pytest backend/tests/test_repository.py -v
```

## ✨ Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/

# Sort imports
isort app/ tests/
```

## 📖 Documentation

- **API Documentation**: `/docs/API.md`
  - Complete REST API reference
  - Request/response examples
  - Error handling

- **Setup Guide**: `/docs/SETUP.md`
  - Installation instructions
  - Configuration
  - Troubleshooting

- **Architecture**: `/docs/ARCHITECTURE.md`
  - System design
  - Component interactions
  - Data flow

- **Contributing**: `/CONTRIBUTING.md`
  - Development guidelines
  - Code style
  - PR process

## 🔄 Workflow

```
User uploads receipt
    ↓
OCRService extracts text
    ↓
LLMService parses details
    ↓
LLMService categorizes
    ↓
ExpenseService saves
    ↓
Return response
    ↓
Frontend displays
```

## 🔧 Configuration

Key environment variables in `.env`:
```
API_HOST=0.0.0.0
API_PORT=8000
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
DATABASE_URL=sqlite:///./finsight.db
TESSERACT_PATH=/usr/local/bin/tesseract
LOG_LEVEL=INFO
```

## 📈 Performance Considerations

1. **Database**: Indexed queries for fast lookups
2. **Async**: FastAPI async endpoints
3. **Caching**: Ready for Redis integration
4. **OCR**: Image preprocessing optimization
5. **LLM**: Temperature tuning for consistency

## 🔒 Security Features

1. Input validation (Pydantic)
2. File type checking
3. File size limits
4. CORS configuration
5. Error handling (no info leakage)

## 🚢 Deployment Ready

- Docker and Docker Compose support
- Production configuration examples
- Environment-based settings
- Logging and monitoring setup
- Error handling and recovery

## 📋 Future Enhancements

1. **Authentication**: JWT/OAuth
2. **Database**: PostgreSQL for production
3. **Features**: Budget tracking, forecasting
4. **Integrations**: Bank APIs, payment platforms
5. **Frontend**: Mobile app
6. **Performance**: Caching, rate limiting
7. **Analytics**: Advanced reporting

## 📄 License

MIT License - See LICENSE file

## 👥 Contributing

Contributions welcome! See CONTRIBUTING.md for guidelines.

## 📞 Support

- API Docs: http://localhost:8000/docs
- GitHub Issues: Report bugs and features
- Documentation: See `/docs` directory

---

**Version**: 0.1.0
**Last Updated**: 2024-03-13
**Status**: Production Ready
