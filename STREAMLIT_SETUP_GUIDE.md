# FinSight AI - Streamlit Dashboard Setup & Usage Guide

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** March 2024

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
cd "FinSight AI"
pip install -r streamlit_requirements.txt
```

### Step 2: Start the API Server (in another terminal)
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 3: Run the Streamlit Dashboard
```bash
streamlit run streamlit_app.py
```

### Step 4: Open in Browser
```
http://localhost:8501
```

**That's it! Your dashboard is now running. 🎉**

---

## 📋 System Requirements

### Minimum Requirements
- Python 3.8+
- 2GB RAM
- Modern web browser
- FastAPI backend running on port 8000

### Recommended Requirements
- Python 3.9+
- 4GB RAM
- Chrome/Firefox/Safari latest version
- SSD for faster performance

---

## 📦 Installation Instructions

### Option 1: Standard Installation

```bash
# Navigate to project directory
cd "FinSight AI"

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r streamlit_requirements.txt
```

### Option 2: Docker Installation

```bash
# Build Docker image
docker build -t finsight-dashboard -f Dockerfile.streamlit .

# Run container
docker run -p 8501:8501 -p 8000:8000 finsight-dashboard
```

### Option 3: Development Installation

```bash
# Install with development dependencies
pip install -r streamlit_requirements.txt
pip install black flake8 pytest pytest-cov
```

---

## 🎯 Running the Dashboard

### Basic Startup

```bash
streamlit run streamlit_app.py
```

### With Configuration

```bash
# Run with custom port
streamlit run streamlit_app.py --server.port 8502

# Run in headless mode (no browser)
streamlit run streamlit_app.py --server.headless true

# Run with custom API URL
streamlit run streamlit_app.py
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# .env
STREAMLIT_API_URL=http://localhost:8000/api
STREAMLIT_LOG_LEVEL=info
```

---

## 📊 Dashboard Features

### 1. 📊 Dashboard Overview
- **Total Spending** - Cumulative spending for selected period
- **Daily Average** - Average spending per day
- **Transaction Count** - Number of transactions
- **Top Category** - Highest spending category
- **Visual Charts** - Pie chart and bar chart visualizations
- **Category Details** - Detailed breakdown with totals and percentages

### 2. 📸 Upload Receipt
- **Image Upload** - Upload receipt images (JPG, PNG, GIF, BMP)
- **Auto-Analysis** - Automatic OCR and expense extraction
- **Confidence Score** - Extract confidence percentage
- **Extracted Details** - Merchant, amount, category, date
- **Instant Save** - Automatically saves to system

### 3. ➕ Add Expense
- **Manual Entry** - Enter expenses manually
- **Date Selection** - Choose expense date
- **Category Selection** - 8 predefined categories
- **Merchant Input** - Store/vendor name
- **Amount Entry** - Expense amount with validation
- **Optional Notes** - Add descriptions for expenses
- **Instant Save** - Immediately available in dashboard

### 4. 📈 Analytics
- **Category Analysis** - Detailed spending by category
- **Spending Trends** - Visualized trends over time
- **Distribution** - Percentage breakdown charts
- **Top Categories** - Ranking of spending categories
- **Summary Table** - Comprehensive data table
- **Interactive Charts** - Hover for detailed information

### 5. 💡 AI Insights
- **Spending Trends** - Overall trend analysis
- **AI Recommendations** - Cost-saving suggestions
- **Budget Alerts** - Category-specific budget status
- **Monthly Analysis** - Month-by-month breakdown
- **Priority Levels** - High/Medium/Low priority recommendations
- **Savings Potential** - Estimated savings for each recommendation

---

## 🎨 UI Components

### Header
- Application title and tagline
- Clean gradient background
- Professional branding

### Sidebar
- **Navigation** - 5 main pages accessible from sidebar
- **Settings** - API configuration options
- **Time Period** - Adjustable analysis period (1-365 days)
- **Quick Access** - Fast switching between pages

### Cards & Metrics
- **Key Metrics** - Large, easy-to-read numbers
- **Category Badges** - Color-coded category indicators
- **Progress Indicators** - Visual budget status

### Charts
- **Pie Charts** - Category distribution
- **Bar Charts** - Amount comparison
- **Interactive Visualizations** - Hover details and zoom
- **Color Coding** - Consistent category colors

### Forms
- **Input Validation** - Real-time validation
- **Date Picker** - Easy date selection
- **Category Selector** - Dropdown with 8 categories
- **File Upload** - Drag-and-drop support

---

## 🔧 Configuration

### API Settings

The dashboard connects to the FastAPI backend. Configure the API URL in the sidebar:

```
Default: http://localhost:8000/api
```

To change the API URL:
1. Click "API Settings" in sidebar
2. Enter your API URL
3. Changes apply immediately

### Dashboard Settings

```python
# streamlit_app.py configuration options:

# Change page title
st.set_page_config(
    page_title="Your Dashboard Title",
    page_icon="🏠"
)

# Change theme colors
PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#ff7f0e"
```

---

## 📱 Responsive Design

The dashboard is fully responsive and works on:
- ✅ Desktop (1920x1080 and higher)
- ✅ Laptop (1366x768)
- ✅ Tablet (768x1024)
- ✅ Mobile (320x568) - Limited features

### Mobile Optimization
```
• Sidebar collapses on mobile
• Charts scale to screen width
• Touch-friendly buttons
• Optimized form inputs
```

---

## 🔐 Security

### API Authentication
Currently, the dashboard connects to the API without authentication. For production, implement:

```python
# Add authentication to requests
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}
response = requests.get(url, headers=headers)
```

### Data Privacy
- No data stored locally (except session cache)
- All data sent to backend API
- HTTPS recommended for production
- API credentials should be environment variables

---

## 🧪 Testing

### Manual Testing Checklist

```
☐ Receipt Upload
  ☐ Test with JPG image
  ☐ Test with PNG image
  ☐ Test with oversized file
  ☐ Verify extracted data

☐ Add Expense
  ☐ Test all categories
  ☐ Test date validation
  ☐ Test amount validation
  ☐ Test with/without description

☐ Dashboard
  ☐ Metrics display correctly
  ☐ Charts render properly
  ☐ Numbers update when expenses added
  ☐ Period selector works

☐ Analytics
  ☐ Category analysis shows all categories
  ☐ Trends display correctly
  ☐ Percentages sum to 100%
  ☐ Sorting works correctly

☐ AI Insights
  ☐ Trends display
  ☐ Recommendations show
  ☐ Budget alerts appear
  ☐ Monthly data loads
```

### Automated Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=streamlit_app

# Run specific test
pytest tests/test_dashboard.py::test_metrics
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused"
**Problem:** API server not running  
**Solution:**
```bash
# Start API server
cd backend
uvicorn main:app --reload --port 8000
```

### Issue: "Module not found"
**Problem:** Dependencies not installed  
**Solution:**
```bash
pip install -r streamlit_requirements.txt
```

### Issue: "Port already in use"
**Problem:** Port 8501 is already in use  
**Solution:**
```bash
# Use different port
streamlit run streamlit_app.py --server.port 8502
```

### Issue: "API URL not accessible"
**Problem:** Incorrect API URL configuration  
**Solution:**
1. Click "API Settings" in sidebar
2. Verify URL: `http://localhost:8000/api`
3. Ensure API server is running
4. Check firewall settings

### Issue: "Images not uploading"
**Problem:** File type or size issue  
**Solution:**
- Ensure file is JPG, PNG, GIF, or BMP
- Check file size is under 10MB
- Verify API has OCR dependencies installed

---

## 📊 Performance Optimization

### Caching
The dashboard uses Streamlit's caching for better performance:

```python
@st.cache_data(ttl=300)
def get_spending_summary(days):
    # Results cached for 5 minutes
    return api_call()
```

### Tips for Better Performance
1. **Reduce Analysis Period** - Smaller date ranges load faster
2. **Limit API Calls** - Avoid rapid page changes
3. **Use Chrome** - Better performance than other browsers
4. **Clear Cache** - Press R in dashboard to clear cache
5. **Restart Streamlit** - Occasional restart improves performance

---

## 🚀 Deployment

### Streamlit Cloud Deployment

```bash
# 1. Push code to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# 2. Deploy on Streamlit Cloud
# Visit: https://share.streamlit.io/
# Connect GitHub account
# Select repository
# Select main branch
# Select streamlit_app.py
```

### Self-Hosted Deployment

```bash
# Using Nginx reverse proxy
server {
    listen 443 ssl;
    server_name dashboard.example.com;
    
    location / {
        proxy_pass http://localhost:8501;
    }
}
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

---

## 🔗 Integration with Backend

### API Endpoints Used

| Endpoint | Purpose | Used In |
|----------|---------|---------|
| `POST /upload-receipt` | Upload receipt | Receipt Upload page |
| `POST /add-expense` | Add expense | Add Expense page |
| `GET /spending-summary` | Get summary | Dashboard & Analytics |
| `GET /monthly-insights` | Get insights | AI Insights page |
| `GET /health` | Health check | Connection verification |

### Custom API Integration

To integrate with your own API:

```python
# Modify API URL in sidebar or code
API_URL = "https://your-api.com/api"

# Update API calls
response = requests.get(f"{API_URL}/spending-summary")
```

---

## 📚 Code Structure

```
streamlit_app.py
├── Imports & Configuration
├── Page Setup (st.set_page_config)
├── CSS Styling
├── Session State Initialization
├── Utility Functions
│   ├── upload_receipt()
│   ├── add_expense()
│   ├── get_spending_summary()
│   └── get_monthly_insights()
├── Header Section
├── Sidebar Navigation
└── Page Content (5 pages)
    ├── Dashboard
    ├── Upload Receipt
    ├── Add Expense
    ├── Analytics
    └── AI Insights
```

---

## 🎓 Usage Examples

### Example 1: Tracking Daily Expenses

```
1. Open dashboard
2. Click "Add Expense" in sidebar
3. Enter date, merchant, category, amount
4. Click "Add Expense"
5. View updated dashboard
```

### Example 2: Uploading Receipt

```
1. Click "Upload Receipt" in sidebar
2. Upload receipt image
3. Click "Analyze Receipt"
4. Review extracted information
5. Confirm to save
```

### Example 3: Viewing Analytics

```
1. Click "Analytics" in sidebar
2. View category analysis
3. Check spending trends
4. Review percentage breakdown
```

### Example 4: Getting Recommendations

```
1. Click "AI Insights" in sidebar
2. Review spending trends
3. Check recommendations by priority
4. Monitor budget alerts
5. Plan spending adjustments
```

---

## 🔄 Updates & Maintenance

### Updating Dependencies

```bash
# Update all packages
pip install --upgrade -r streamlit_requirements.txt

# Update specific package
pip install --upgrade streamlit
```

### Checking for Updates

```bash
# Check for outdated packages
pip list --outdated

# Update all outdated packages
pip install -U $(pip list --outdated | awk 'NR>2 {print $1}')
```

---

## 📞 Support & Feedback

### Reporting Issues
1. Check troubleshooting guide above
2. Check Streamlit documentation
3. Check API documentation
4. Review dashboard logs

### Getting Help
- **Streamlit Docs:** https://docs.streamlit.io/
- **API Docs:** http://localhost:8000/docs
- **GitHub Issues:** Report bugs and request features

---

## 🎯 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `R` | Clear cache |
| `C` | Clear console |
| `P` | Open settings |
| `Shift+M` | Open menu |

---

## 📊 System Monitoring

### Check API Status
```bash
curl http://localhost:8000/api/health
```

### Monitor Dashboard Logs
```bash
# View Streamlit logs
streamlit logs

# View with timestamp
streamlit run streamlit_app.py --logger.level=debug
```

---

## ✅ Pre-Launch Checklist

Before deploying to production:

- [ ] API server tested and working
- [ ] Dashboard features verified
- [ ] All categories properly configured
- [ ] Charts and visualizations working
- [ ] Forms validating correctly
- [ ] API error handling tested
- [ ] Performance acceptable
- [ ] Security review completed
- [ ] Documentation updated
- [ ] User training completed

---

## 🎉 Summary

Your FinSight AI Streamlit Dashboard is now ready to use! 

**Quick Reference:**
1. Start API: `cd backend && uvicorn main:app --reload`
2. Start Dashboard: `streamlit run streamlit_app.py`
3. Open Browser: `http://localhost:8501`

**Features:**
- 📊 Beautiful dashboard with real-time metrics
- 📸 Receipt upload with OCR
- ➕ Manual expense entry
- 📈 Detailed analytics and charts
- 💡 AI-powered recommendations
- 🎨 Modern, clean UI design

**Next Steps:**
1. Explore all features
2. Start tracking expenses
3. Monitor spending patterns
4. Review AI recommendations
5. Optimize your budget

---

**Happy tracking! 💰📊🎉**

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** March 2024
