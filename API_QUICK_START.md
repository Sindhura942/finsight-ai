# FinSight AI - API Quick Start Guide

## 🚀 Getting Started

This guide will help you quickly integrate and test the FinSight AI API.

---

## 📋 Prerequisites

- Python 3.8+
- FastAPI installed
- SQLAlchemy installed
- Running database instance

---

## 🔧 Installation

### 1. Install Dependencies

```bash
cd backend
pip install fastapi uvicorn sqlalchemy python-multipart pillow pytesseract
```

### 2. Start the API Server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

### 3. API Documentation

FastAPI automatically generates interactive documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📊 Core Endpoints

### Receipt Upload

Upload a receipt image for automatic analysis:

```bash
curl -X POST "http://localhost:8000/api/upload-receipt" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.jpg"
```

**Response:**
```json
{
  "success": true,
  "expense": {
    "id": 1,
    "date": "2024-03-13",
    "merchant": "Starbucks",
    "category": "food & dining",
    "amount": 6.50
  },
  "confidence": 0.95
}
```

---

### Manual Expense Entry

Add an expense via text input:

```bash
curl -X POST "http://localhost:8000/api/add-expense" \
  -d "date=2024-03-13&merchant=Starbucks&category=food&amount=6.50"
```

**Parameters:**
- `date` (required): YYYY-MM-DD format
- `merchant` (required): Store/vendor name
- `category` (required): Expense category
- `amount` (required): Amount in decimal format
- `description` (optional): Notes

---

### Spending Summary

Get categorized expense breakdown:

```bash
curl "http://localhost:8000/api/spending-summary?days=30"
```

**Returns:**
- Total spending and averages
- Breakdown by category
- Spending percentage per category
- AI-generated insights

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

### Monthly Insights

Get detailed trends and recommendations:

```bash
curl "http://localhost:8000/api/monthly-insights?months=3"
```

**Returns:**
- Monthly spending trends
- Month-over-month comparison
- AI recommendations with savings potential
- Budget alerts

**Response:**
```json
{
  "success": true,
  "monthly_data": [...],
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

## 🔍 Query Parameters

### Common Parameters

| Parameter | Type | Default | Max | Usage |
|-----------|------|---------|-----|-------|
| `days` | integer | 30 | 365 | Spending summary, trends, recommendations |
| `months` | integer | 3 | 12 | Monthly insights |
| `category` | string | - | - | Filter by category |

### Examples

```bash
# Last 90 days
curl "http://localhost:8000/api/spending-summary?days=90"

# Last year
curl "http://localhost:8000/api/spending-summary?days=365"

# Filter by category
curl "http://localhost:8000/api/expenses?days=30&category=food"

# 6 months of insights
curl "http://localhost:8000/api/monthly-insights?months=6"
```

---

## 🐍 Python Usage Examples

### Basic Setup

```python
import requests

BASE_URL = "http://localhost:8000/api"

def upload_receipt(file_path):
    """Upload a receipt image"""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"{BASE_URL}/upload-receipt",
            files=files
        )
    return response.json()

def add_expense(date, merchant, category, amount, description=""):
    """Add manual expense"""
    response = requests.post(
        f"{BASE_URL}/add-expense",
        params={
            'date': date,
            'merchant': merchant,
            'category': category,
            'amount': amount,
            'description': description
        }
    )
    return response.json()

def get_spending_summary(days=30):
    """Get spending summary"""
    response = requests.get(
        f"{BASE_URL}/spending-summary",
        params={'days': days}
    )
    return response.json()

def get_monthly_insights(months=3):
    """Get monthly insights"""
    response = requests.get(
        f"{BASE_URL}/monthly-insights",
        params={'months': months}
    )
    return response.json()

def get_recommendations(days=30):
    """Get cost-saving recommendations"""
    response = requests.get(
        f"{BASE_URL}/recommendations",
        params={'days': days}
    )
    return response.json()
```

### Full Workflow

```python
# 1. Upload a receipt
result = upload_receipt('receipt.jpg')
print(f"Uploaded: {result['expense']['merchant']} - ${result['expense']['amount']}")

# 2. Add manual expense
result = add_expense(
    date='2024-03-13',
    merchant='Whole Foods',
    category='groceries',
    amount=75.50
)
print(f"Added: {result['message']}")

# 3. Get spending summary
summary = get_spending_summary(days=30)
print(f"Total spending (30 days): ${summary['summary']['total_spending']}")
for cat in summary['by_category']:
    print(f"  {cat['category']}: ${cat['total']} ({cat['percentage']}%)")

# 4. Get insights
insights = get_monthly_insights(months=3)
print(f"Overall trend: {insights['trends']['overall_trend']}")
for rec in insights['recommendations']:
    print(f"  [{rec['priority']}] {rec['suggestion']}")
    print(f"    Potential savings: ${rec['potential_savings']}")

# 5. Get recommendations
recs = get_recommendations(days=30)
print(f"Total potential savings: ${recs['summary']['total_potential_savings']}")
```

---

## 📱 JavaScript/Node.js Usage

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Upload receipt
async function uploadReceipt(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${BASE_URL}/upload-receipt`, {
    method: 'POST',
    body: formData
  });
  return response.json();
}

// Add expense
async function addExpense(date, merchant, category, amount, description = '') {
  const params = new URLSearchParams({
    date,
    merchant,
    category,
    amount,
    description
  });
  
  const response = await fetch(`${BASE_URL}/add-expense?${params}`, {
    method: 'POST'
  });
  return response.json();
}

// Get spending summary
async function getSpendingSummary(days = 30) {
  const response = await fetch(`${BASE_URL}/spending-summary?days=${days}`);
  return response.json();
}

// Get monthly insights
async function getMonthlyInsights(months = 3) {
  const response = await fetch(`${BASE_URL}/monthly-insights?months=${months}`);
  return response.json();
}

// Get recommendations
async function getRecommendations(days = 30) {
  const response = await fetch(`${BASE_URL}/recommendations?days=${days}`);
  return response.json();
}

// Usage
async function main() {
  // Upload receipt
  const fileInput = document.querySelector('input[type="file"]');
  const result = await uploadReceipt(fileInput.files[0]);
  console.log('Uploaded:', result.expense);
  
  // Get summary
  const summary = await getSpendingSummary(30);
  console.log('Total spending:', summary.summary.total_spending);
  
  // Get insights
  const insights = await getMonthlyInsights(3);
  console.log('Trend:', insights.trends.overall_trend);
}
```

---

## 🧪 Testing with Postman

### Import Collection

1. Download `POSTMAN_COLLECTION.json` from the project root
2. Open Postman
3. Click "Import" → Select the JSON file
4. All endpoints are now ready to test

### Manual Testing

1. Start the API server
2. Open Postman
3. Create a new request
4. Enter endpoint URL (e.g., `http://localhost:8000/api/spending-summary`)
5. Set query parameters
6. Click "Send"

---

## 📈 Response Format

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

### Error Responses

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Status Codes

- `200` - Successful GET request
- `201` - Successful POST request (resource created)
- `400` - Bad request (invalid input)
- `413` - File too large
- `422` - Validation error
- `500` - Server error

---

## 🔗 Integration Tips

### Rate Limiting (Future)

Currently no rate limiting. Future versions will include:
- 100 requests/minute per IP
- 1000 requests/hour per API key

### Timeout Handling

```python
import requests

try:
    response = requests.get(
        'http://localhost:8000/api/spending-summary',
        params={'days': 30},
        timeout=10
    )
    data = response.json()
except requests.Timeout:
    print("Request timeout - API took too long to respond")
except requests.RequestException as e:
    print(f"Request error: {e}")
```

### Error Handling

```python
response = requests.get('http://localhost:8000/api/spending-summary')

if response.status_code == 200:
    data = response.json()
    print(f"Success: {data['summary']['total_spending']}")
elif response.status_code == 422:
    print(f"Validation error: {response.json()}")
elif response.status_code == 500:
    print("Server error - try again later")
```

---

## 📚 Full API Documentation

For complete API documentation, see: `API_ENDPOINTS_DOCUMENTATION.md`

---

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Module Not Found Errors

```bash
# Ensure all dependencies are installed
pip install fastapi uvicorn sqlalchemy python-multipart pillow pytesseract
```

### Database Connection Issues

```python
# Verify database is running
# Check database connection string in config
# Ensure SQLAlchemy session is properly configured
```

### File Upload Not Working

- Ensure file is under 10MB
- Verify file format (JPG, PNG, GIF, BMP)
- Check multipart/form-data header is set

---

## ✅ Next Steps

1. ✅ API server is running
2. ✅ Test endpoints with curl or Postman
3. ✅ Integrate with frontend application
4. ✅ Set up error handling and retry logic
5. ✅ Monitor API performance
6. ✅ Implement caching for frequently accessed data
7. ✅ Add authentication (API keys/JWT)
8. ✅ Deploy to production

---

## 📞 Support

- **Documentation:** See `API_ENDPOINTS_DOCUMENTATION.md`
- **Postman Collection:** Import `POSTMAN_COLLECTION.json`
- **Code Examples:** See above
- **Issues:** Check existing errors and logs

---

**Last Updated:** March 2024  
**Version:** 1.0.0
