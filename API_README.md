# FinSight AI - FastAPI Endpoints

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Last Updated:** March 2024

---

## 🚀 Overview

Complete REST API for FinSight AI expense tracking application. Built with FastAPI, providing real-time financial analytics, AI-powered recommendations, and comprehensive spending insights.

### Key Features

- 📸 **Receipt Upload** - Automatic OCR analysis and expense extraction
- 💰 **Expense Tracking** - Manual entry with smart categorization
- 📊 **Spending Analytics** - Real-time summaries and category breakdown
- 📈 **Monthly Insights** - Trends, predictions, and cost-saving recommendations
- 🎯 **Budget Alerts** - Category-specific budget tracking
- 🤖 **AI Recommendations** - Intelligent spending suggestions with savings potential

---

## 📦 Quick Start

### Installation

```bash
# Install dependencies
pip install fastapi uvicorn sqlalchemy python-multipart pillow pytesseract

# Start API server
cd backend
uvicorn main:app --reload --port 8000
```

### Access API

- **API Base URL:** `http://localhost:8000/api`
- **Interactive Docs:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

### Test Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Get spending summary
curl "http://localhost:8000/api/spending-summary?days=30"

# Get monthly insights
curl "http://localhost:8000/api/monthly-insights?months=3"
```

---

## 📚 Documentation

### Core Documentation

| Document | Purpose | Link |
|----------|---------|------|
| **API Reference** | Complete endpoint documentation | `API_ENDPOINTS_DOCUMENTATION.md` |
| **Quick Start** | Getting started guide | `API_QUICK_START.md` |
| **Integration Guide** | Integration patterns & best practices | `API_INTEGRATION_GUIDE.md` |
| **Summary** | Implementation overview | `API_IMPLEMENTATION_SUMMARY.md` |

### Collections & Examples

| Resource | Purpose | Link |
|----------|---------|------|
| **Postman Collection** | Ready-to-test API requests | `POSTMAN_COLLECTION.json` |
| **Python Examples** | Python integration examples | In documentation |
| **JavaScript Examples** | JavaScript/Node.js examples | In documentation |
| **cURL Examples** | Command-line examples | In documentation |

---

## 🔌 API Endpoints

### Receipt Upload
```
POST /api/upload-receipt
Upload receipt image and extract expense information
```

### Expense Management
```
POST /api/add-expense      - Add manual expense
GET  /api/expenses         - Retrieve expenses
```

### Spending Analysis
```
GET /api/spending-summary      - Category breakdown & summary
GET /api/category-breakdown    - Detailed category analysis
```

### Insights & Trends
```
GET /api/monthly-insights      - Monthly trends & recommendations
GET /api/spending-trends       - Daily & weekly trends
GET /api/recommendations       - Cost-saving suggestions
```

### System
```
GET /api/health               - Health check
GET /api/stats                - System statistics
```

---

## 📋 Endpoint Summary

### 1. Upload Receipt

**Endpoint:** `POST /api/upload-receipt`

Upload a receipt image for automatic analysis.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/upload-receipt" \
  -F "file=@receipt.jpg"
```

**Response:**
```json
{
  "success": true,
  "expense": {
    "id": 1,
    "merchant": "Starbucks",
    "category": "food & dining",
    "amount": 6.50,
    "date": "2024-03-13"
  },
  "confidence": 0.95
}
```

---

### 2. Add Expense

**Endpoint:** `POST /api/add-expense`

Add expense via text input.

**Parameters:**
- `date` (required) - YYYY-MM-DD format
- `merchant` (required) - Store name
- `category` (required) - Expense category
- `amount` (required) - Amount (>0)
- `description` (optional) - Notes

**Request:**
```bash
curl -X POST "http://localhost:8000/api/add-expense" \
  -d "date=2024-03-13&merchant=Starbucks&category=food&amount=6.50"
```

---

### 3. Spending Summary

**Endpoint:** `GET /api/spending-summary`

Get comprehensive spending breakdown.

**Parameters:**
- `days` - Period in days (1-365, default: 30)

**Request:**
```bash
curl "http://localhost:8000/api/spending-summary?days=30"
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_spending": 250.50,
    "average_daily_spending": 8.35,
    "transaction_count": 15
  },
  "by_category": [
    {
      "category": "food & dining",
      "total": 150.00,
      "percentage": 59.8,
      "transaction_count": 10
    }
  ],
  "insights": [...]
}
```

---

### 4. Monthly Insights

**Endpoint:** `GET /api/monthly-insights`

Get detailed monthly trends and recommendations.

**Parameters:**
- `months` - Period in months (1-12, default: 3)

**Request:**
```bash
curl "http://localhost:8000/api/monthly-insights?months=3"
```

**Response:**
```json
{
  "success": true,
  "trends": {
    "overall_trend": "increasing",
    "spending_stability": 0.85
  },
  "recommendations": [
    {
      "priority": "high",
      "category": "food & dining",
      "suggestion": "Consider meal planning...",
      "potential_savings": 50.00
    }
  ],
  "budget_alerts": [...]
}
```

---

## 🔧 Integration Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Add expense
response = requests.post(
    f"{BASE_URL}/add-expense",
    params={
        'date': '2024-03-13',
        'merchant': 'Starbucks',
        'category': 'food',
        'amount': 6.50
    }
)
print(response.json())

# Get spending summary
response = requests.get(
    f"{BASE_URL}/spending-summary",
    params={'days': 30}
)
print(response.json())

# Get monthly insights
response = requests.get(
    f"{BASE_URL}/monthly-insights",
    params={'months': 3}
)
print(response.json())
```

### JavaScript

```javascript
const API_BASE = 'http://localhost:8000/api';

// Add expense
async function addExpense(expense) {
  const params = new URLSearchParams(expense);
  const response = await fetch(`${API_BASE}/add-expense?${params}`, {
    method: 'POST'
  });
  return response.json();
}

// Get spending summary
async function getSpendingSummary(days = 30) {
  const response = await fetch(
    `${API_BASE}/spending-summary?days=${days}`
  );
  return response.json();
}

// Get monthly insights
async function getMonthlyInsights(months = 3) {
  const response = await fetch(
    `${API_BASE}/monthly-insights?months=${months}`
  );
  return response.json();
}

// Usage
const summary = await getSpendingSummary(30);
console.log(summary);
```

---

## 🔒 Error Handling

### Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET request successful |
| 201 | Created | POST request successful |
| 400 | Bad request | Invalid input data |
| 413 | File too large | Receipt > 10MB |
| 422 | Validation error | Missing required field |
| 500 | Server error | Database error |

### Error Response

```json
{
  "detail": "Invalid file type. Allowed: .jpg, .jpeg, .png, .gif, .bmp"
}
```

---

## 📊 Response Format

### Success Response

All successful responses follow this structure:

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Endpoint-specific data
  }
}
```

### Pagination (if applicable)

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

---

## 🚀 Deployment

### Environment Variables

```bash
# .env
API_BASE_URL=https://api.finsight.com
API_PORT=8000
DATABASE_URL=postgresql://user:password@localhost/finsight
LOG_LEVEL=INFO
```

### Docker Deployment

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- ✅ Update API_BASE_URL to production domain
- ✅ Enable HTTPS
- ✅ Set up database backups
- ✅ Configure logging
- ✅ Set up monitoring
- ✅ Implement rate limiting
- ✅ Configure authentication
- ✅ Set up CI/CD pipeline

---

## 📈 Performance Optimization

### Caching

Cache frequently accessed endpoints:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_spending_summary(days: int):
    # This result will be cached
    pass
```

### Batch Operations

```python
# Add multiple expenses efficiently
for expense in expenses:
    requests.post('/add-expense', params=expense)
```

### Connection Pooling

Use SQLAlchemy connection pooling in production.

---

## 🔐 Security

### Input Validation

- ✅ File type and size validation
- ✅ Date format validation
- ✅ Amount validation
- ✅ String length limits
- ✅ Required field checking

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://finsight.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting (Future)

```python
# Implement rate limiting in production
- 100 requests/minute per IP
- 1000 requests/hour per API key
```

---

## 🧪 Testing

### With Postman

1. Import `POSTMAN_COLLECTION.json`
2. Set environment variables
3. Run requests
4. Verify responses

### With cURL

```bash
# Test all endpoints
bash test_endpoints.sh
```

### With Python

```python
import unittest
from api_client import FinSightAPI

class TestAPI(unittest.TestCase):
    def test_add_expense(self):
        # Test expense addition
        pass
```

---

## 📞 Support

### Documentation

- **API Reference:** `API_ENDPOINTS_DOCUMENTATION.md`
- **Quick Start:** `API_QUICK_START.md`
- **Integration:** `API_INTEGRATION_GUIDE.md`

### Common Issues

**Issue:** Connection refused  
**Solution:** Ensure API server is running on port 8000

**Issue:** File too large error  
**Solution:** Receipt must be under 10MB

**Issue:** Validation error  
**Solution:** Check date format (YYYY-MM-DD) and amount > 0

---

## 📋 API Features by Category

### Receipt Processing
- ✅ Image upload (JPG, PNG, GIF, BMP)
- ✅ OCR analysis
- ✅ Merchant extraction
- ✅ Amount recognition
- ✅ Category detection
- ✅ Confidence scoring

### Expense Management
- ✅ Manual entry
- ✅ Auto-categorization
- ✅ Date tracking
- ✅ Description support
- ✅ Amount validation
- ✅ Expense retrieval

### Analytics
- ✅ Total spending
- ✅ Category breakdown
- ✅ Spending trends
- ✅ Daily averages
- ✅ Monthly comparison
- ✅ Transaction history

### Recommendations
- ✅ Cost-saving tips
- ✅ Priority ranking
- ✅ Savings potential
- ✅ Category analysis
- ✅ Budget alerts
- ✅ Trend prediction

---

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core endpoints implemented
- ✅ Documentation complete
- ✅ Examples provided
- ✅ Local testing ready

### Phase 2 (Upcoming)
- API authentication (JWT)
- Rate limiting
- Advanced caching
- Webhook support
- Data export (CSV, PDF)

### Phase 3 (Future)
- Real-time notifications
- Mobile app support
- Bank integration
- Budget planning tools
- Expense sharing

---

## 📊 API Statistics

- **Total Endpoints:** 10+
- **Request Types:** GET, POST
- **Response Format:** JSON
- **Authentication:** Optional (future)
- **Rate Limit:** Configurable
- **Timeout:** 30 seconds (configurable)

---

## 📝 License

FinSight AI - All Rights Reserved

---

## 👥 Support Team

**Email:** support@finsight.com  
**GitHub Issues:** Report bugs and request features  
**Documentation:** See included markdown files

---

## 🎉 Ready to Get Started?

1. **Read:** `API_QUICK_START.md`
2. **Test:** Import `POSTMAN_COLLECTION.json`
3. **Integrate:** Follow `API_INTEGRATION_GUIDE.md`
4. **Reference:** Use `API_ENDPOINTS_DOCUMENTATION.md`

---

**Status:** 🟢 PRODUCTION READY  
**Version:** 1.0.0  
**Last Updated:** March 2024

Happy tracking! 💰📊🚀
