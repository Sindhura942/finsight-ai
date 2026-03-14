"""QUICK REFERENCE - FinSight AI

Essential commands and information for developers.
"""

## 🚀 Start Development Environment

### macOS/Linux
```bash
# Setup (one-time)
chmod +x setup.sh
./setup.sh

# Start all services
# Terminal 1
ollama serve

# Terminal 2
cd backend && source venv/bin/activate && python main.py

# Terminal 3
cd frontend && source venv/bin/activate && streamlit run app.py
```

### Windows
```bash
# Setup (one-time)
setup.bat

# Start all services
# CMD 1
ollama serve

# CMD 2
cd backend && venv\Scripts\activate.bat && python main.py

# CMD 3
cd frontend && venv\Scripts\activate.bat && streamlit run app.py
```

## 🔗 Access Points

- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/
- **Dashboard**: http://localhost:8501
- **Ollama API**: http://localhost:11434

## 📝 Common Commands

### Backend

```bash
cd backend
source venv/bin/activate          # Activate environment

python main.py                    # Run API server
pytest tests/ -v                  # Run tests
pytest tests/ -v --cov           # Run tests with coverage
black app/ tests/                 # Format code
flake8 app/ tests/               # Lint code
mypy app/                         # Type checking
```

### Frontend

```bash
cd frontend
source venv/bin/activate          # Activate environment

streamlit run app.py              # Run dashboard
```

### Database

```bash
# Access SQLite database
sqlite3 finsight.db

# List tables
.tables

# Exit
.quit
```

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Stop and remove volumes
docker-compose down -v
```

## 📂 Important Files

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI application entry point |
| `frontend/app.py` | Streamlit application |
| `.env` | Environment configuration |
| `backend/app/services/` | Business logic layer |
| `backend/app/api/` | API endpoints |
| `backend/app/database/` | Database layer |

## 🔌 API Quick Tests

```bash
# Health check
curl http://localhost:8000/api/health/

# Get all expenses
curl http://localhost:8000/api/expenses/

# Get spending summary
curl http://localhost:8000/api/insights/spending-summary?days=30

# Create expense
curl -X POST http://localhost:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_name": "Starbucks",
    "amount": 5.50,
    "category": "Food & Dining"
  }'
```

## 📊 Database Schema

**expenses table**
- `id` (primary key)
- `merchant_name` (indexed)
- `amount`
- `category` (indexed)
- `date` (indexed)
- `description`
- `image_path`
- `confidence_score`
- `created_at` (indexed)
- `updated_at`

## 🎯 Main Components

```
FastAPI Backend
├── API Routes (expenses, insights, health)
├── Services (OCR, LLM, Expense, Insight)
├── Database (SQLite + SQLAlchemy)
├── Models (Pydantic schemas)
└── Workflows (LangGraph orchestration)

Streamlit Frontend
├── Dashboard
├── Upload Receipt
├── Expenses List
├── Analytics
└── Recommendations
```

## 🔧 Configuration (.env)

```env
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
DATABASE_URL=sqlite:///./finsight.db
TESSERACT_PATH=/usr/local/bin/tesseract
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific test
pytest backend/tests/test_repository.py::test_create_expense -v

# Run with coverage report
pytest backend/tests/ --cov=app --cov-report=html
```

## 📦 Package Management

```bash
# Add new package
pip install package_name
pip freeze > requirements.txt

# Update all packages
pip install --upgrade -r requirements.txt

# Check for vulnerabilities
pip-audit
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama connection error | Run `ollama serve` in another terminal |
| Tesseract not found | Install: `brew install tesseract` |
| Port already in use | Change port in `.env` or kill process: `lsof -i :8000` |
| Database locked | Ensure only one backend instance running |
| Module not found | Activate venv and reinstall: `pip install -r requirements.txt` |

## 📚 Documentation Files

- `README.md` - Project overview
- `PROJECT_SUMMARY.md` - Complete summary
- `docs/API.md` - API reference
- `docs/SETUP.md` - Installation guide
- `docs/ARCHITECTURE.md` - System design
- `CONTRIBUTING.md` - Contribution guidelines

## 🎓 Learning Resources

1. **FastAPI**: https://fastapi.tiangolo.com/
2. **Streamlit**: https://streamlit.io/docs
3. **SQLAlchemy**: https://docs.sqlalchemy.org/
4. **LangGraph**: https://langchain.readthedocs.io/
5. **Ollama**: https://ollama.ai

## ✅ Pre-commit Checklist

Before committing code:
```bash
# Format code
black app/ tests/
isort app/ tests/

# Check quality
flake8 app/ tests/
mypy app/

# Run tests
pytest tests/ -v

# Check for issues
git status
```

## 🚀 Deployment Checklist

- [ ] Set `API_DEBUG=false`
- [ ] Use production database (PostgreSQL)
- [ ] Add authentication
- [ ] Enable HTTPS/SSL
- [ ] Add rate limiting
- [ ] Setup monitoring/logging
- [ ] Configure backups
- [ ] Load test the application
- [ ] Security audit
- [ ] Update documentation

## 📞 Getting Help

1. Check documentation in `/docs/`
2. Review API docs at http://localhost:8000/docs
3. Check GitHub issues
4. Review example code in tests

---

**Quick Links**:
- [Project Summary](PROJECT_SUMMARY.md)
- [API Documentation](docs/API.md)
- [Setup Instructions](docs/SETUP.md)
- [Architecture](docs/ARCHITECTURE.md)
