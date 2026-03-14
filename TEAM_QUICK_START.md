# 🚀 Quick Start Checklist for Team Members

## ✅ What You're Getting

- **Complete FinSight AI Application** (production-ready)
- **Runnable Code** with all dependencies
- **Interactive Dashboard** (Streamlit)
- **REST API** with documentation
- **SQLite Database** (initialized and ready)
- **Comprehensive Documentation** (13+ guides)

---

## 📋 Setup Checklist (10-15 minutes)

Follow these steps in order:

### 1. Extract/Clone the Project
```bash
# If ZIP file:
unzip finsight-app.zip
cd "FinSight AI"

# If GitHub:
git clone <repository-url>
cd finsight-ai
```

### 2. Create Virtual Environment
```bash
# Create venv
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see: (venv) prefix in your terminal
```

### 3. Install Dependencies
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies (if separate)
# Most dependencies are shared
```

**✅ Check**: All packages installed without errors
- Expected: 24 packages
- Time: 2-5 minutes

### 4. Verify Database Setup
```bash
cd backend
python3 << 'EOF'
from app.database.models import ExpenseORM
from app.database.session import Base, engine
Base.metadata.create_all(bind=engine)
print("✅ Database initialized!")
EOF
cd ..
```

**✅ Check**: "✅ Database initialized!" appears
- Creates `finsight.db` file
- Sets up `expenses` table

### 5. Start Backend Server
```bash
# In terminal 1:
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Check**: You see:
```
Uvicorn running on http://127.0.0.1:8000
```

### 6. Start Dashboard (New Terminal)
```bash
# In terminal 2:
# Make sure venv is activated first
source venv/bin/activate
streamlit run streamlit_app.py
```

**✅ Check**: Dashboard opens automatically in browser at http://localhost:8501

### 7. Verify Everything Works

#### Test 1: API Health Check
```bash
# In terminal 3:
curl http://localhost:8000/api/expenses/
# Should return: []
```

#### Test 2: Access API Docs
```
Open: http://localhost:8000/docs
You should see Swagger UI with all endpoints
```

#### Test 3: Dashboard
```
Dashboard at http://localhost:8501 should load without errors
```

#### Test 4: Add Sample Data
```bash
# Via API:
curl -X POST http://localhost:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{
    "merchant": "Coffee Shop",
    "amount": 5.50,
    "category": "Food",
    "description": "Morning coffee"
  }'

# Or via Dashboard UI
```

**✅ Check**: Data appears in dashboard or API response

---

## 🎯 Usage Guide

### Via Dashboard (Easiest)
1. Go to http://localhost:8501
2. Click "Add Expense" 
3. Fill in details
4. Click "Save"
5. View analytics in real-time

### Via API (Programmatic)
```bash
# Add expense
curl -X POST http://localhost:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{...}'

# Get all expenses
curl http://localhost:8000/api/expenses/

# Get spending summary
curl http://localhost:8000/api/insights/spending-summary?days=30
```

### API Documentation
Visit http://localhost:8000/docs for interactive documentation

---

## ⚠️ Common Issues & Fixes

### Issue: "Address already in use"
**Solution**: Another app is using that port
```bash
# Kill the process
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn main:app --port 8001
```

### Issue: "no such table: expenses"
**Solution**: Database not initialized
```bash
cd backend
python3 << 'EOF'
from app.database.models import ExpenseORM
from app.database.session import Base, engine
Base.metadata.create_all(bind=engine)
EOF
```

### Issue: ModuleNotFoundError
**Solution**: Activate virtual environment
```bash
source venv/bin/activate
```

### Issue: Can't access http://localhost:8501
**Solution**: Streamlit didn't start
```bash
# Check if running:
ps aux | grep streamlit

# Restart:
streamlit run streamlit_app.py
```

### Issue: API endpoint returning 404
**Solution**: Make sure you're using correct endpoint
```bash
# Correct:
http://localhost:8000/api/expenses/

# Incorrect:
http://localhost:8000/expenses/
http://localhost:8000/api/v1/expenses/
```

---

## 📚 Documentation Files

Read these for more details:

| File | Purpose | Read Time |
|------|---------|-----------|
| **HOW_TO_RUN_PROPERLY.md** | Detailed running instructions | 10 min |
| **PROJECT_LOCATIONS.md** | Where everything is | 5 min |
| **SERVICE_IMPLEMENTATION_GUIDE.md** | Architecture details | 15 min |
| **TESTING_GUIDE.md** | How to test | 10 min |
| **DEPLOYMENT_GUIDE.md** | How to deploy | 15 min |

---

## 🔄 Daily Usage

### Start the App
```bash
# Always from project root
cd "/path/to/FinSight AI"

# Activate venv
source venv/bin/activate

# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Dashboard (new terminal)
streamlit run streamlit_app.py
```

### Access
- Dashboard: http://localhost:8501
- API Docs: http://localhost:8000/docs
- API: http://localhost:8000/api/...

### Stop the App
```bash
# Press Ctrl+C in each terminal
# Or kill processes:
kill -9 $(lsof -t -i :8000)
kill -9 $(lsof -t -i :8501)
```

---

## 🆘 Need Help?

### Check This First
1. Is virtual environment activated? (`source venv/bin/activate`)
2. Are both servers running? (Check terminal output)
3. Are ports 8000 and 8501 available?
4. Did you initialize the database?

### Still Stuck?
1. Check logs in terminal where app is running
2. Read HOW_TO_RUN_PROPERLY.md for detailed troubleshooting
3. Check browser console (F12) for frontend errors
4. Verify API is responding: `curl http://localhost:8000/api/expenses/`

---

## 📦 Project Structure

```
FinSight AI/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── finsight.db               # Database (created automatically)
│   ├── requirements.txt           # Backend dependencies
│   └── app/
│       ├── api/                  # REST endpoints
│       ├── services/             # Business logic
│       ├── database/             # Database models
│       └── core/                 # Configuration
│
├── streamlit_app.py              # Dashboard
├── venv/                         # Virtual environment
├── requirements.txt              # Project dependencies
└── docs/                         # Documentation
    ├── HOW_TO_RUN_PROPERLY.md
    ├── HOW_TO_SHARE_AND_RUN.md
    └── ... (more guides)
```

---

## ✅ Success Checklist

- [ ] Virtual environment created and activated
- [ ] All dependencies installed (24 packages)
- [ ] Database initialized (finsight.db created)
- [ ] FastAPI running on port 8000
- [ ] Streamlit running on port 8501
- [ ] Can access dashboard at http://localhost:8501
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can add an expense
- [ ] Can view data in dashboard

---

## 🚀 Ready to Go!

Once all checks pass, you're ready to:
- ✅ Use the application
- ✅ Add your financial data
- ✅ Get insights from the AI
- ✅ Collaborate with team
- ✅ Deploy to production (see DEPLOYMENT_GUIDE.md)

---

## 💡 Pro Tips

1. **Keep servers running** in background during development
2. **Check API docs** at http://localhost:8000/docs for all endpoints
3. **Use browser console** (F12) to debug dashboard issues
4. **Check terminal logs** for API/server errors
5. **Create new terminal** for each long-running service
6. **Deactivate venv** when done: `deactivate`

---

## 📞 Support Resources

- **API Documentation**: http://localhost:8000/docs (when running)
- **Code Comments**: See `backend/app/` for inline documentation
- **Guides**: Read the `.md` files in project root
- **Examples**: Check test curl commands in this file

---

**Welcome to FinSight AI! Happy coding! 🎉**

Questions? Read HOW_TO_RUN_PROPERLY.md for detailed troubleshooting.
