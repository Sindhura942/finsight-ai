# 🚀 How to Run FinSight AI Properly

## ✅ Database Setup (Already Done)

The database has been initialized with the `expenses` table. The database file is located at:
```
/Users/sindhuram/Downloads/FinSight AI/backend/finsight.db
```

## 📋 Prerequisites

Make sure you have:
- Python 3.13 installed
- Virtual environment activated: `source venv/bin/activate`

## 🎯 Running the Application

### Option 1: Run from Separate Terminals (Recommended)

**Terminal 1 - FastAPI Backend:**
```bash
cd "/Users/sindhuram/Downloads/FinSight AI/backend"
source ../venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Streamlit Dashboard:**
```bash
cd "/Users/sindhuram/Downloads/FinSight AI"
source venv/bin/activate
streamlit run streamlit_app.py
```

### Option 2: Run Both from Project Root (Using Background Tasks)

```bash
cd "/Users/sindhuram/Downloads/FinSight AI"
source venv/bin/activate

# Start FastAPI in background
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &

# Go back to project root
cd ..

# Start Streamlit
streamlit run streamlit_app.py
```

## 🌐 Access Points

Once running:

| Service | URL | Purpose |
|---------|-----|---------|
| **API Documentation** | http://localhost:8000/docs | Interactive API docs (Swagger UI) |
| **API Health Check** | http://localhost:8000/health | Check if API is running |
| **Dashboard** | http://localhost:8501 | Streamlit dashboard |

## 📝 Important Notes

### 1. **Working Directory Matters**
- **FastAPI** must run from `/backend` folder because the database file `finsight.db` is created relative to that directory
- **Streamlit** can run from project root

### 2. **Virtual Environment**
- Always activate the virtual environment before running:
  ```bash
  source venv/bin/activate
  ```
- You'll see `(venv)` prefix in your terminal when activated

### 3. **Port Availability**
- FastAPI uses port **8000** - make sure it's not in use
- Streamlit uses port **8501** - make sure it's not in use
- If ports are occupied, use flags:
  ```bash
  uvicorn main:app --port 8001  # Use port 8001 instead
  streamlit run streamlit_app.py --server.port 8502  # Use port 8502
  ```

### 4. **Database File Location**
```
✅ Correct location: /Users/sindhuram/Downloads/FinSight AI/backend/finsight.db
❌ Wrong location: /Users/sindhuram/Downloads/FinSight AI/finsight.db
```

The database file will be automatically created the first time you run the backend if it doesn't exist.

## 🧪 Testing the Setup

### Test 1: Check FastAPI is running
```bash
curl http://localhost:8000/health
# Should return: {"status": "ok"}
```

### Test 2: Check API endpoints
```bash
curl http://localhost:8000/api/expenses/
# Should return: []
```

### Test 3: Access Dashboard
Open browser to http://localhost:8501

## 🐛 Troubleshooting

### Issue: "Address already in use"
```bash
# Find process using port 8000
lsof -i :8000

# Kill it if needed
kill -9 <PID>
```

### Issue: "No module named 'app'"
Make sure you're in the `/backend` folder when running FastAPI:
```bash
cd backend
uvicorn main:app --reload
```

### Issue: "no such table: expenses"
Run this from the backend folder:
```bash
python3 << 'EOF'
from app.database.models import ExpenseORM
from app.database.session import Base, engine
Base.metadata.create_all(bind=engine)
print("✅ Database tables created")
EOF
```

### Issue: Streamlit can't connect to API
1. Make sure FastAPI is running first
2. Check that it's accessible: `curl http://localhost:8000/docs`
3. Verify the API URL in `streamlit_app.py` is correct: `http://localhost:8000/api`

## 📊 Testing the Full Stack

1. **Start FastAPI Backend:**
   ```bash
   cd backend && uvicorn main:app --reload
   ```

2. **Start Streamlit Dashboard** (in new terminal):
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Test by adding an expense:**
   - Go to http://localhost:8501
   - Navigate to "Add Expense" section
   - Fill in details and submit
   - You should see it appear in the dashboard

4. **Verify via API:**
   ```bash
   curl http://localhost:8000/api/expenses/
   # Should show the expense you just added
   ```

## 🔄 Development Workflow

### Making Code Changes
- **Backend changes**: Uvicorn auto-reloads with `--reload` flag
- **Dashboard changes**: Streamlit auto-detects changes and reloads

### Checking Logs
- **FastAPI logs**: Shown in terminal where uvicorn is running
- **Streamlit logs**: Shown in terminal where streamlit is running, also in browser console

### Database Changes
- Tables are created automatically from models
- To reset database, delete `backend/finsight.db` and restart the app
- To add new models, add them to `backend/app/database/models.py` and restart

## 📦 Project Structure (For Reference)

```
/Users/sindhuram/Downloads/FinSight AI/
├── backend/                          # FastAPI application
│   ├── app/
│   │   ├── api/                     # API endpoints
│   │   ├── services/                # Business logic
│   │   ├── database/                # Database models and session
│   │   └── core/                    # Configuration
│   ├── main.py                      # FastAPI app entry point
│   ├── requirements.txt             # Backend dependencies
│   └── finsight.db                  # SQLite database (created at runtime)
│
├── streamlit_app.py                 # Streamlit dashboard entry point
├── venv/                            # Virtual environment
├── requirements.txt                 # Dashboard/frontend dependencies
└── docs/                            # Documentation (HOW_TO_SHARE_AND_RUN.md, etc)
```

## 🚀 Quick Start (TL;DR)

```bash
# 1. Navigate to project
cd "/Users/sindhuram/Downloads/FinSight AI"

# 2. Activate virtual environment
source venv/bin/activate

# 3. Terminal 1: Start Backend
cd backend
uvicorn main:app --reload

# 4. Terminal 2: Start Dashboard (NEW TERMINAL)
cd .. # Go back to project root
streamlit run streamlit_app.py

# 5. Open browser
# API: http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

---

**Status: ✅ Database initialized and tested. All systems ready to run!**

Last Updated: $(date)
