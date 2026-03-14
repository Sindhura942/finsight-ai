"""API Documentation - FinSight AI"""

## API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
Currently no authentication. Add JWT/OAuth as needed for production.

---

## Expense Endpoints

### Upload Receipt Image
```
POST /api/expenses/upload
```

**Request:**
- Content-Type: `multipart/form-data`
- File: Receipt image (JPG, PNG, etc., max 10MB)

**Response (200 OK):**
```json
{
  "id": 1,
  "merchant_name": "Starbucks",
  "amount": 5.50,
  "category": "Food & Dining",
  "date": "2024-03-13T10:30:00",
  "description": "Coffee and breakfast",
  "image_path": "/uploads/receipt_123.jpg",
  "confidence_score": 0.95,
  "created_at": "2024-03-13T10:35:00",
  "updated_at": "2024-03-13T10:35:00"
}
```

**Error (400 Bad Request):**
```json
{
  "detail": "File type not allowed. Allowed types: ['.jpg', '.jpeg', '.png', '.gif', '.bmp']"
}
```

---

### Create Expense
```
POST /api/expenses/
```

**Request:**
```json
{
  "merchant_name": "Starbucks",
  "amount": 5.50,
  "category": "Food & Dining",
  "date": "2024-03-13T10:30:00",
  "description": "Coffee and breakfast",
  "confidence_score": 1.0
}
```

**Response (200 OK):** Same as upload endpoint

---

### Get Expenses
```
GET /api/expenses/
```

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Max records to return (default: 100)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "merchant_name": "Starbucks",
    "amount": 5.50,
    "category": "Food & Dining",
    ...
  }
]
```

---

### Get Expense by ID
```
GET /api/expenses/{id}
```

**Response (200 OK):** Single expense object

**Error (404 Not Found):**
```json
{
  "detail": "Expense not found"
}
```

---

### Update Expense
```
PUT /api/expenses/{id}
```

**Request:** (All fields optional)
```json
{
  "merchant_name": "Updated Store",
  "amount": 10.00,
  "category": "Shopping",
  "description": "Updated description"
}
```

**Response (200 OK):** Updated expense object

---

### Delete Expense
```
DELETE /api/expenses/{id}
```

**Response (200 OK):**
```json
{
  "message": "Expense deleted successfully"
}
```

---

## Insights Endpoints

### Get Spending Summary
```
GET /api/insights/spending-summary
```

**Query Parameters:**
- `days`: Analysis period in days (1-365, default: 30)

**Response (200 OK):**
```json
{
  "total_spending": 590.00,
  "transaction_count": 25,
  "average_transaction": 23.60,
  "highest_category": "Food & Dining",
  "period": "Last 30 days",
  "categories": [
    {
      "category": "Food & Dining",
      "total_amount": 150.50,
      "transaction_count": 10,
      "average_transaction": 15.05,
      "percentage_of_total": 25.5
    }
  ]
}
```

---

### Get Spending by Category
```
GET /api/insights/by-category
```

**Query Parameters:**
- `days`: Analysis period in days (1-365, default: 30)

**Response (200 OK):**
```json
[
  {
    "category": "Food & Dining",
    "total_amount": 150.50,
    "transaction_count": 10,
    "average_transaction": 15.05,
    "percentage_of_total": 25.5
  }
]
```

---

### Get Spending Trends
```
GET /api/insights/trends
```

**Query Parameters:**
- `days`: Analysis period in days (1-365, default: 30)

**Response (200 OK):**
```json
[
  {
    "date": "2024-03-10T00:00:00",
    "amount": 50.00,
    "category": "Food & Dining"
  },
  {
    "date": "2024-03-11T00:00:00",
    "amount": 75.50,
    "category": "Shopping"
  }
]
```

---

### Get Recommendations
```
POST /api/insights/recommendations
```

**Request:**
```json
{
  "days": 30,
  "category": null
}
```

**Response (200 OK):**
```json
{
  "suggestions": [
    {
      "title": "Reduce dining frequency",
      "description": "You spent $150 on Food & Dining. Consider cooking at home 2-3 times more per week.",
      "potential_savings": 30.00,
      "category": "Food & Dining",
      "priority": "high"
    }
  ],
  "total_potential_savings": 100.00,
  "analysis_period": "Last 30 days"
}
```

---

## Health Endpoints

### Health Check
```
GET /api/health/
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "database": "ok",
  "llm_service": "ok"
}
```

**Response (200 OK - Degraded):**
```json
{
  "status": "degraded",
  "database": "error",
  "llm_service": "ok"
}
```

---

## Error Handling

All error responses follow this format:

```json
{
  "detail": "Error message describing the issue"
}
```

**Common Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - File too large
- `500 Internal Server Error` - Server error

---

## Rate Limiting (Future)

Recommended limits:
- 100 requests per minute per IP
- 10 file uploads per minute

---

## Examples

### Using cURL

Upload receipt:
```bash
curl -X POST http://localhost:8000/api/expenses/upload \
  -F "file=@receipt.jpg"
```

Get spending summary:
```bash
curl http://localhost:8000/api/insights/spending-summary?days=30
```

Create expense:
```bash
curl -X POST http://localhost:8000/api/expenses/ \
  -H "Content-Type: application/json" \
  -d '{
    "merchant_name": "Starbucks",
    "amount": 5.50,
    "category": "Food & Dining"
  }'
```

### Using Python

```python
import requests

# Upload receipt
files = {"file": open("receipt.jpg", "rb")}
response = requests.post("http://localhost:8000/api/expenses/upload", files=files)
print(response.json())

# Get summary
response = requests.get("http://localhost:8000/api/insights/spending-summary?days=30")
print(response.json())
```

---

## Pagination

List endpoints support pagination:

```
GET /api/expenses/?skip=20&limit=10
```

This returns 10 items starting from the 21st record.
