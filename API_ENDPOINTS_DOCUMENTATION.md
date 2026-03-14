# FinSight AI - FastAPI Endpoints Documentation

**Version:** 1.0.0  
**Last Updated:** March 2024  
**Status:** Production Ready

## 📋 Table of Contents

1. [Overview](#overview)
2. [Base URL & Authentication](#base-url--authentication)
3. [Receipt Upload Endpoints](#receipt-upload-endpoints)
4. [Expense Management](#expense-management)
5. [Spending Summary](#spending-summary)
6. [Monthly Insights](#monthly-insights)
7. [Response Formats](#response-formats)
8. [Error Handling](#error-handling)
9. [Examples](#examples)

---

## Overview

The FinSight AI API provides comprehensive expense tracking and financial insights. All endpoints return JSON responses with consistent structure.

### Key Features

- ✅ Receipt image upload and OCR analysis
- ✅ Manual expense entry via text
- ✅ Real-time spending summaries
- ✅ AI-powered cost-saving recommendations
- ✅ Monthly spending trends and analytics
- ✅ Category-based breakdown
- ✅ Budget tracking and alerts

### API Version

- **Current:** 1.0.0
- **Base Path:** `/api`

---

## Base URL & Authentication

### Endpoint Structure

```
Base URL: http://localhost:8000/api
Protocol: HTTP/HTTPS (depending on environment)
Default Port: 8000
Content-Type: application/json
```

### Authentication

Currently no authentication required. Future versions will support:
- API Key authentication
- OAuth 2.0
- JWT tokens

---

## Receipt Upload Endpoints

### POST /upload-receipt

Upload a receipt image and run complete analysis.

**Endpoint:** `POST /api/upload-receipt`

**Content-Type:** `multipart/form-data`

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes | Receipt image (JPG, PNG, GIF, BMP) |

**File Requirements:**
- Maximum size: 10MB
- Allowed formats: .jpg, .jpeg, .png, .gif, .bmp
- Minimum resolution: 200x200 pixels (recommended: 1000x1000)

**Response (201 Created):**

```json
{
  "success": true,
  "message": "Receipt analyzed and stored successfully",
  "expense": {
    "id": 1,
    "date": "2024-03-13",
    "merchant": "Starbucks",
    "category": "food & dining",
    "amount": 6.50,
    "description": "Coffee",
    "source": "receipt_upload",
    "created_at": "2024-03-13T10:30:00Z"
  },
  "confidence": 0.95,
  "extraction_details": {
    "merchant_confidence": 0.98,
    "amount_confidence": 0.99,
    "category_confidence": 0.90
  }
}
```

**Error Responses:**

```json
// 400 - Bad Request
{
  "detail": "Invalid file type. Allowed: .jpg, .jpeg, .png, .gif, .bmp"
}

// 413 - File Too Large
{
  "detail": "File too large. Maximum size is 10MB"
}

// 422 - Unprocessable Entity
{
  "detail": "Failed to process receipt image"
}
```

**cURL Example:**

```bash
curl -X POST "http://localhost:8000/api/upload-receipt" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@receipt.jpg"
```

**Python Example:**

```python
import requests

with open('receipt.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/upload-receipt',
        files=files
    )
    print(response.json())
```

**JavaScript Example:**

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:8000/api/upload-receipt', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data);
```

---

## Expense Management

### POST /add-expense

Add a new expense via text input (manual entry).

**Endpoint:** `POST /api/add-expense`

**Content-Type:** `application/x-www-form-urlencoded`

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| date | string | Yes | Date in YYYY-MM-DD format |
| merchant | string | Yes | Vendor/store name |
| category | string | Yes | Expense category |
| amount | number | Yes | Amount (must be > 0) |
| description | string | No | Optional notes |

**Response (201 Created):**

```json
{
  "success": true,
  "message": "Expense added successfully",
  "expense": {
    "id": 1,
    "date": "2024-03-13",
    "merchant": "Starbucks",
    "category": "food & dining",
    "amount": 6.50,
    "description": "Morning coffee",
    "source": "manual_entry",
    "created_at": "2024-03-13T10:30:00Z"
  }
}
```

**cURL Example:**

```bash
# Basic
curl -X POST "http://localhost:8000/api/add-expense?date=2024-03-13&merchant=Starbucks&category=food&amount=6.50"

# With description
curl -X POST "http://localhost:8000/api/add-expense" \
  -d "date=2024-03-13&merchant=Whole Foods&category=groceries&amount=75.50&description=Weekly groceries"
```

**Python Example:**

```python
import requests

response = requests.post(
    'http://localhost:8000/api/add-expense',
    params={
        'date': '2024-03-13',
        'merchant': 'Starbucks',
        'category': 'food',
        'amount': 6.50,
        'description': 'Morning coffee'
    }
)
print(response.json())
```

---

### GET /expenses

Retrieve all expenses for a period.

**Endpoint:** `GET /api/expenses`

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| days | integer | 30 | Number of days (1-365) |
| category | string | None | Filter by category (optional) |

**Response:**

```json
{
  "success": true,
  "count": 15,
  "total_amount": 250.50,
  "period": {
    "from": "2024-02-13",
    "to": "2024-03-13"
  },
  "expenses": [
    {
      "id": 1,
      "date": "2024-03-13",
      "merchant": "Starbucks",
      "category": "food & dining",
      "amount": 6.50,
      "description": "Coffee",
      "source": "receipt_upload"
    }
  ]
}
```

**Examples:**

```bash
# Last 30 days (default)
curl "http://localhost:8000/api/expenses"

# Last 90 days
curl "http://localhost:8000/api/expenses?days=90"

# Filter by category
curl "http://localhost:8000/api/expenses?days=30&category=food"
```

---

## Spending Summary

### GET /spending-summary

Get comprehensive spending summary with categorized breakdown.

**Endpoint:** `GET /api/spending-summary`

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| days | integer | 30 | Number of days (1-365) |

**Response:**

```json
{
  "success": true,
  "period_days": 30,
  "summary": {
    "total_spending": 250.50,
    "average_daily_spending": 8.35,
    "transaction_count": 15,
    "highest_category": "food & dining",
    "date_range": {
      "from": "2024-02-13",
      "to": "2024-03-13"
    }
  },
  "by_category": [
    {
      "category": "food & dining",
      "total": 150.00,
      "percentage": 59.8,
      "transaction_count": 10,
      "average_per_transaction": 15.00,
      "last_transaction": "2024-03-13"
    }
  ],
  "insights": [
    "Food & dining is your top spending category (59.8%)",
    "You spent an average of $8.35 per day"
  ]
}
```

**Examples:**

```bash
curl "http://localhost:8000/api/spending-summary"
curl "http://localhost:8000/api/spending-summary?days=90"
curl "http://localhost:8000/api/spending-summary?days=365"
```

---

### GET /category-breakdown

Get detailed breakdown by category with transaction details.

**Endpoint:** `GET /api/category-breakdown`

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| days | integer | 30 | Number of days (1-365) |

**Response:**

```json
{
  "success": true,
  "period_days": 30,
  "categories": [
    {
      "category": "food & dining",
      "total": 150.00,
      "percentage": 59.8,
      "transaction_count": 10,
      "average_per_transaction": 15.00,
      "min_transaction": 5.50,
      "max_transaction": 45.00,
      "last_transaction": "2024-03-13",
      "transactions": [
        {
          "date": "2024-03-13",
          "merchant": "Starbucks",
          "amount": 6.50
        }
      ]
    }
  ]
}
```

---

## Monthly Insights

### GET /monthly-insights

Get detailed monthly spending trends and AI recommendations.

**Endpoint:** `GET /api/monthly-insights`

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| months | integer | 3 | Number of months (1-12) |

**Response:**

```json
{
  "success": true,
  "analysis_period": "3 months",
  "monthly_data": [
    {
      "month": "2024-01",
      "total_spending": 850.00,
      "transaction_count": 35,
      "average_daily": 27.42,
      "vs_previous_month": {
        "change_amount": 50.00,
        "change_percentage": 6.3,
        "direction": "up"
      },
      "top_categories": [
        {
          "category": "food & dining",
          "amount": 350.00,
          "percentage": 41.2
        }
      ]
    }
  ],
  "trends": {
    "overall_trend": "increasing",
    "trend_description": "Your spending is increasing.",
    "fastest_growing_category": "transportation",
    "most_consistent_category": "food & dining",
    "spending_stability": 0.85
  },
  "recommendations": [
    {
      "priority": "high",
      "category": "food & dining",
      "suggestion": "Consider meal planning to reduce food spending.",
      "potential_savings": 50.00,
      "savings_percentage": 14.3
    }
  ],
  "budget_alerts": [
    {
      "category": "food & dining",
      "suggested_budget": 300.00,
      "current_spending": 350.00,
      "status": "over_budget",
      "excess_amount": 50.00
    }
  ]
}
```

**Examples:**

```bash
curl "http://localhost:8000/api/monthly-insights"
curl "http://localhost:8000/api/monthly-insights?months=6"
curl "http://localhost:8000/api/monthly-insights?months=12"
```

---

### GET /spending-trends

Get detailed daily/weekly spending trends.

**Endpoint:** `GET /api/spending-trends`

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| days | integer | 30 | Number of days (1-365) |

**Response:**

```json
{
  "success": true,
  "period_days": 30,
  "daily_trends": [
    {
      "date": "2024-03-13",
      "total": 25.50,
      "transaction_count": 3,
      "categories": {
        "food & dining": 15.50,
        "transportation": 10.00
      }
    }
  ],
  "weekly_summary": [
    {
      "week": "2024-W11",
      "total": 180.00,
      "average_daily": 25.71,
      "transaction_count": 20
    }
  ]
}
```

---

### GET /recommendations

Get AI-powered cost-saving recommendations.

**Endpoint:** `GET /api/recommendations`

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| days | integer | 30 | Number of days (1-365) |
| category | string | None | Specific category (optional) |

**Response:**

```json
{
  "success": true,
  "period_days": 30,
  "recommendations": [
    {
      "id": "rec_001",
      "priority": "high",
      "category": "food & dining",
      "current_spending": 150.00,
      "suggested_budget": 120.00,
      "potential_savings": 30.00,
      "savings_percentage": 20.0,
      "suggestion": "You're spending more on food than average.",
      "actions": [
        "Set a weekly food budget",
        "Plan meals for the week",
        "Cook at home instead of eating out"
      ]
    }
  ],
  "summary": {
    "total_potential_savings": 105.00,
    "high_priority_count": 2,
    "medium_priority_count": 1,
    "low_priority_count": 0
  }
}
```

---

## Response Formats

### Success Response Structure

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { }
}
```

### Error Response Structure

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": { }
  }
}
```

### Pagination (if applicable)

```json
{
  "success": true,
  "data": [ ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK | GET request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid credentials |
| 404 | Not Found | Resource not found |
| 413 | Payload Too Large | File exceeds max size |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |

### Error Response Example

```json
{
  "detail": "Invalid file type. Allowed: .jpg, .jpeg, .png, .gif, .bmp"
}
```

---

## Examples

### Full Workflow Example

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. Upload a receipt
with open('receipt.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        f"{BASE_URL}/upload-receipt",
        files=files
    )
    print("Upload Response:", response.json())

# 2. Add manual expense
response = requests.post(
    f"{BASE_URL}/add-expense",
    params={
        'date': '2024-03-13',
        'merchant': 'Whole Foods',
        'category': 'groceries',
        'amount': 75.50,
        'description': 'Weekly groceries'
    }
)
print("Add Expense Response:", response.json())

# 3. Get spending summary
response = requests.get(
    f"{BASE_URL}/spending-summary",
    params={'days': 30}
)
print("Spending Summary:", response.json())

# 4. Get monthly insights
response = requests.get(
    f"{BASE_URL}/monthly-insights",
    params={'months': 3}
)
print("Monthly Insights:", response.json())

# 5. Get recommendations
response = requests.get(
    f"{BASE_URL}/recommendations",
    params={'days': 30}
)
print("Recommendations:", response.json())
```

---

## Rate Limiting

Currently no rate limiting implemented. Future versions will include:
- 100 requests per minute per IP
- 1000 requests per hour per API key
- Burst allowance: 20 requests

---

## Versioning

API uses URL versioning:

```
/api/v1/endpoint  # Version 1
/api/v2/endpoint  # Version 2 (future)
```

Current version: `/api` (v1)

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/your-repo/issues
- Email: support@finsightai.com
- Documentation: https://docs.finsightai.com

---

**Last Updated:** March 2024  
**Version:** 1.0.0  
**Status:** Production Ready
