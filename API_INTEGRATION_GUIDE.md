# FinSight AI - API Integration Guide

## 📖 Complete Integration Documentation

This guide covers everything needed to integrate the FinSight AI API with your frontend or other services.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Integration Patterns](#integration-patterns)
3. [Frontend Integration](#frontend-integration)
4. [Error Handling & Retry Logic](#error-handling--retry-logic)
5. [Performance Optimization](#performance-optimization)
6. [Security Considerations](#security-considerations)
7. [Testing & Validation](#testing--validation)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────┐
│         Frontend Application            │
│  (Web/Mobile Client)                    │
└──────────────┬──────────────────────────┘
               │
               │ HTTP/REST
               │
┌──────────────▼──────────────────────────┐
│         FastAPI Server                  │
│  (http://localhost:8000/api)            │
│                                          │
│  ├── Receipt Upload Endpoints           │
│  ├── Expense Management                 │
│  ├── Spending Summary                   │
│  ├── Monthly Insights                   │
│  └── Health/Status                      │
└──────────────┬──────────────────────────┘
               │
               │ SQLAlchemy ORM
               │
┌──────────────▼──────────────────────────┐
│         Database                        │
│  (PostgreSQL/SQLite/MySQL)              │
│                                          │
│  ├── Expenses Table                     │
│  ├── Categories Table                   │
│  ├── Transactions Table                 │
│  └── Insights Cache Table               │
└─────────────────────────────────────────┘
```

### Request/Response Flow

```
Frontend Request
    │
    ├─ Validate input locally
    ├─ Add authentication headers
    ├─ Set Content-Type header
    │
    ▼
API Endpoint
    │
    ├─ Validate request data
    ├─ Check authentication
    ├─ Process business logic
    │
    ▼
Service Layer
    │
    ├─ ExpenseService
    ├─ InsightService
    ├─ OCRService (for receipt processing)
    │
    ▼
Database
    │
    ├─ Query/Update data
    ├─ Cache results
    │
    ▼
Response
    │
    ├─ JSON formatted response
    ├─ Appropriate HTTP status code
    │
    ▼
Frontend
    │
    ├─ Parse response
    ├─ Update UI
    ├─ Handle errors
```

---

## Integration Patterns

### 1. Request/Response Pattern

#### Standard Request Structure

```javascript
const request = {
  method: 'GET' | 'POST',
  url: 'http://localhost:8000/api/endpoint',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer <token>' // Future
  },
  params: {
    // Query parameters
  },
  data: {
    // Request body (POST/PUT)
  }
};
```

#### Standard Response Structure

**Success (2xx):**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    // Endpoint-specific data
  }
}
```

**Error (4xx/5xx):**
```json
{
  "detail": "Error message"
}
```

### 2. Error Response Handling Pattern

```python
def handle_response(response):
    """Unified response handler"""
    
    if response.status_code in [200, 201]:
        return {
            'success': True,
            'data': response.json()
        }
    
    elif response.status_code == 400:
        return {
            'success': False,
            'error': 'Bad request - invalid input',
            'details': response.json()
        }
    
    elif response.status_code == 413:
        return {
            'success': False,
            'error': 'File too large',
            'max_size': '10MB'
        }
    
    elif response.status_code == 422:
        return {
            'success': False,
            'error': 'Validation failed',
            'details': response.json()
        }
    
    elif response.status_code == 500:
        return {
            'success': False,
            'error': 'Server error',
            'retry': True
        }
    
    else:
        return {
            'success': False,
            'error': f'Unknown error: {response.status_code}'
        }
```

### 3. Data Transformation Pattern

```python
class APIResponse:
    """Unified API response handler"""
    
    def __init__(self, response):
        self.response = response
        self.status_code = response.status_code
        self.data = response.json()
    
    @property
    def is_success(self):
        return self.status_code in [200, 201]
    
    @property
    def is_error(self):
        return not self.is_success
    
    def get_data(self):
        """Extract actual data from response"""
        if self.is_success:
            return self.data.get('data', self.data)
        return None
    
    def get_error(self):
        """Extract error message"""
        if self.is_error:
            return self.data.get('detail', 'Unknown error')
        return None
```

---

## Frontend Integration

### React/Vue/Angular Integration

#### Vue.js Example

```javascript
// api.js - Centralized API client
import axios from 'axios';

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000/api';

class FinSightAPI {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000
    });
  }

  // Receipt endpoints
  async uploadReceipt(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await this.client.post('/upload-receipt', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Expense endpoints
  async addExpense(expense) {
    try {
      const response = await this.client.post('/add-expense', null, {
        params: {
          date: expense.date,
          merchant: expense.merchant,
          category: expense.category,
          amount: expense.amount,
          description: expense.description
        }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getExpenses(days = 30, category = null) {
    try {
      const response = await this.client.get('/expenses', {
        params: { days, ...(category && { category }) }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Summary endpoints
  async getSpendingSummary(days = 30) {
    try {
      const response = await this.client.get('/spending-summary', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Insights endpoints
  async getMonthlyInsights(months = 3) {
    try {
      const response = await this.client.get('/monthly-insights', {
        params: { months }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getRecommendations(days = 30, category = null) {
    try {
      const response = await this.client.get('/recommendations', {
        params: { days, ...(category && { category }) }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Health check
  async healthCheck() {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      return { status: 'error' };
    }
  }

  // Error handling
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const message = error.response.data?.detail || 'Unknown error';
      
      const errorMap = {
        400: 'Invalid input',
        413: 'File too large',
        422: 'Validation failed',
        500: 'Server error'
      };
      
      return new Error(errorMap[status] || message);
    } else if (error.request) {
      // Request made but no response
      return new Error('No response from server');
    } else {
      // Error in request setup
      return new Error(error.message);
    }
  }
}

export default new FinSightAPI();
```

#### Vue Component Example

```vue
<template>
  <div class="dashboard">
    <!-- Upload Receipt -->
    <section v-if="!loading" class="upload-section">
      <h2>Upload Receipt</h2>
      <input 
        type="file" 
        @change="handleFileUpload"
        accept="image/*"
      />
      <button @click="uploadReceipt" :disabled="!selectedFile">
        Upload
      </button>
      <div v-if="uploadError" class="error">{{ uploadError }}</div>
    </section>

    <!-- Spending Summary -->
    <section v-if="summary" class="summary-section">
      <h2>Spending Summary ({{ summary.period_days }} days)</h2>
      
      <div class="summary-stats">
        <div class="stat">
          <label>Total Spending</label>
          <value>${{ summary.summary.total_spending }}</value>
        </div>
        <div class="stat">
          <label>Daily Average</label>
          <value>${{ summary.summary.average_daily_spending }}</value>
        </div>
        <div class="stat">
          <label>Transactions</label>
          <value>{{ summary.summary.transaction_count }}</value>
        </div>
      </div>

      <!-- Category Breakdown -->
      <div class="categories">
        <h3>By Category</h3>
        <div v-for="cat in summary.by_category" :key="cat.category" class="category">
          <span>{{ cat.category }}</span>
          <span>${{ cat.total }} ({{ cat.percentage }}%)</span>
        </div>
      </div>

      <!-- Insights -->
      <div v-if="summary.insights" class="insights">
        <h3>Insights</h3>
        <ul>
          <li v-for="insight in summary.insights" :key="insight">
            {{ insight }}
          </li>
        </ul>
      </div>
    </section>

    <!-- Monthly Insights -->
    <section v-if="insights" class="insights-section">
      <h2>Monthly Insights</h2>
      
      <!-- Trends -->
      <div v-if="insights.trends" class="trends">
        <h3>Trends</h3>
        <p><strong>Overall:</strong> {{ insights.trends.overall_trend }}</p>
        <p><strong>Stability:</strong> {{ (insights.trends.spending_stability * 100).toFixed(0) }}%</p>
      </div>

      <!-- Recommendations -->
      <div v-if="insights.recommendations" class="recommendations">
        <h3>Recommendations</h3>
        <div 
          v-for="rec in insights.recommendations" 
          :key="rec.suggestion"
          class="recommendation"
          :class="`priority-${rec.priority}`"
        >
          <span class="priority">{{ rec.priority }}</span>
          <p>{{ rec.suggestion }}</p>
          <p class="savings">Potential savings: ${{ rec.potential_savings }}</p>
        </div>
      </div>

      <!-- Budget Alerts -->
      <div v-if="insights.budget_alerts" class="alerts">
        <h3>Budget Alerts</h3>
        <div 
          v-for="alert in insights.budget_alerts" 
          :key="alert.category"
          class="alert"
          :class="`status-${alert.status}`"
        >
          <span>{{ alert.category }}</span>
          <span>{{ alert.current_spending }} / {{ alert.suggested_budget }}</span>
        </div>
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <p>Loading...</p>
    </div>
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'Dashboard',
  data() {
    return {
      selectedFile: null,
      loading: false,
      uploadError: null,
      summary: null,
      insights: null
    };
  },
  computed: {
    summaryDays() {
      return 30;
    },
    insightMonths() {
      return 3;
    }
  },
  methods: {
    async handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
      this.uploadError = null;
    },
    async uploadReceipt() {
      if (!this.selectedFile) return;
      
      this.loading = true;
      try {
        const result = await api.uploadReceipt(this.selectedFile);
        console.log('Receipt uploaded:', result.expense);
        this.selectedFile = null;
        await this.loadSummary();
      } catch (error) {
        this.uploadError = error.message;
      } finally {
        this.loading = false;
      }
    },
    async loadSummary() {
      this.loading = true;
      try {
        this.summary = await api.getSpendingSummary(this.summaryDays);
      } catch (error) {
        console.error('Failed to load summary:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadInsights() {
      this.loading = true;
      try {
        this.insights = await api.getMonthlyInsights(this.insightMonths);
      } catch (error) {
        console.error('Failed to load insights:', error);
      } finally {
        this.loading = false;
      }
    }
  },
  async mounted() {
    await Promise.all([this.loadSummary(), this.loadInsights()]);
  }
};
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat {
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.categories {
  margin-bottom: 30px;
}

.category {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.recommendations {
  margin-bottom: 30px;
}

.recommendation {
  padding: 15px;
  margin-bottom: 10px;
  border-left: 4px solid #ccc;
  border-radius: 4px;
}

.recommendation.priority-high {
  border-left-color: #ff4444;
  background: #fff5f5;
}

.recommendation.priority-medium {
  border-left-color: #ffaa00;
  background: #fffaf0;
}

.recommendation.priority-low {
  border-left-color: #44aa44;
  background: #f5fff5;
}

.priority {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.savings {
  color: #00aa00;
  font-weight: bold;
}

.loading {
  text-align: center;
  padding: 40px;
}
</style>
```

---

## Error Handling & Retry Logic

### Exponential Backoff Retry Strategy

```python
import time
import requests
from typing import Callable, Any

class RetryStrategy:
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 32.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        
        delay = self.initial_delay
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.RequestException as e:
                last_exception = e
                
                # Don't retry on client errors (4xx)
                if hasattr(e, 'response') and e.response and 400 <= e.response.status_code < 500:
                    raise
                
                if attempt < self.max_retries:
                    print(f"Attempt {attempt + 1}/{self.max_retries + 1} failed. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay = min(delay * self.exponential_base, self.max_delay)
        
        raise last_exception


# Usage
retry_strategy = RetryStrategy(max_retries=3)

def get_spending_summary():
    response = requests.get('http://localhost:8000/api/spending-summary')
    return response.json()

try:
    summary = retry_strategy.execute(get_spending_summary)
    print("Success:", summary)
except Exception as e:
    print("Failed after retries:", e)
```

### Circuit Breaker Pattern

```python
from enum import Enum
import time

class CircuitState(Enum):
    CLOSED = 'closed'      # Normal operation
    OPEN = 'open'          # Reject requests
    HALF_OPEN = 'half_open'  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker"""
        
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = CircuitState.HALF_OPEN
                print("Circuit breaker: Attempting recovery...")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"Circuit breaker: OPENED after {self.failure_count} failures")

# Usage
breaker = CircuitBreaker(failure_threshold=5, timeout=60)

def get_summary():
    response = requests.get('http://localhost:8000/api/spending-summary')
    return response.json()

try:
    summary = breaker.call(get_summary)
except Exception as e:
    print("Circuit breaker error:", e)
```

---

## Performance Optimization

### Caching Strategy

```python
import functools
import time
from typing import Any, Callable

class Cache:
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str) -> Any:
        """Get cached value if not expired"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cache value with timestamp"""
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()


# Decorator
def cached(ttl: int = 300):
    cache = Cache(ttl=ttl)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{args}:{kwargs}"
            
            # Check cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(key, result)
            
            return result
        
        wrapper.cache = cache
        return wrapper
    
    return decorator


# Usage
@cached(ttl=300)  # Cache for 5 minutes
def get_spending_summary(days=30):
    response = requests.get(
        'http://localhost:8000/api/spending-summary',
        params={'days': days}
    )
    return response.json()

# Call function
summary = get_spending_summary(days=30)
print(summary)

# Clear cache
get_spending_summary.cache.clear()
```

### Batch Operations

```python
class BatchProcessor:
    def __init__(self, batch_size: int = 10):
        self.batch_size = batch_size
    
    def batch_add_expenses(self, expenses: list) -> list:
        """Add multiple expenses efficiently"""
        results = []
        
        for i in range(0, len(expenses), self.batch_size):
            batch = expenses[i:i + self.batch_size]
            
            for expense in batch:
                response = requests.post(
                    'http://localhost:8000/api/add-expense',
                    params={
                        'date': expense['date'],
                        'merchant': expense['merchant'],
                        'category': expense['category'],
                        'amount': expense['amount'],
                        'description': expense.get('description', '')
                    }
                )
                
                if response.status_code == 201:
                    results.append(response.json()['expense'])
        
        return results

# Usage
processor = BatchProcessor(batch_size=50)
expenses = [
    {'date': '2024-03-13', 'merchant': 'Starbucks', 'category': 'food', 'amount': 6.50},
    # ... more expenses
]
results = processor.batch_add_expenses(expenses)
```

---

## Security Considerations

### Input Validation

```python
from datetime import datetime
import re

class InputValidator:
    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validate YYYY-MM-DD format"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Validate amount is positive and numeric"""
        try:
            amt = float(amount)
            return amt > 0 and amt <= 999999.99
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_merchant(merchant: str) -> bool:
        """Validate merchant name"""
        if not isinstance(merchant, str):
            return False
        merchant = merchant.strip()
        return 1 <= len(merchant) <= 255
    
    @staticmethod
    def validate_category(category: str) -> bool:
        """Validate category"""
        valid_categories = [
            'food & dining',
            'groceries',
            'transportation',
            'utilities',
            'entertainment',
            'shopping',
            'health',
            'other'
        ]
        return category.lower() in valid_categories
    
    @staticmethod
    def validate_file(file) -> bool:
        """Validate uploaded file"""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        
        # Check extension
        filename = file.filename.lower()
        if not any(filename.endswith(ext) for ext in allowed_extensions):
            return False
        
        # Check size (10MB)
        file.seek(0, 2)
        size = file.tell()
        return size <= 10 * 1024 * 1024  # 10MB


# Usage
validator = InputValidator()

if not validator.validate_date('2024-03-13'):
    raise ValueError("Invalid date format")

if not validator.validate_amount(6.50):
    raise ValueError("Invalid amount")

if not validator.validate_merchant('Starbucks'):
    raise ValueError("Invalid merchant")
```

### Rate Limiting (Client-side)

```python
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        # Check if limit exceeded
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True
    
    def wait_if_needed(self) -> None:
        """Wait if rate limit exceeded"""
        while not self.is_allowed():
            time.sleep(0.1)


# Usage
limiter = RateLimiter(max_requests=100, time_window=60)

for i in range(150):
    limiter.wait_if_needed()
    # Make API request
    response = requests.get('http://localhost:8000/api/spending-summary')
```

---

## Testing & Validation

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch
import requests

class TestFinSightAPI(unittest.TestCase):
    
    @patch('requests.post')
    def test_add_expense_success(self, mock_post):
        """Test successful expense addition"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'success': True,
            'expense': {'id': 1, 'merchant': 'Starbucks'}
        }
        mock_post.return_value = mock_response
        
        response = requests.post(
            'http://localhost:8000/api/add-expense',
            params={
                'date': '2024-03-13',
                'merchant': 'Starbucks',
                'category': 'food',
                'amount': 6.50
            }
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()['success'])
    
    @patch('requests.post')
    def test_add_expense_validation_error(self, mock_post):
        """Test expense validation error"""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.json.return_value = {
            'detail': 'Validation error'
        }
        mock_post.return_value = mock_response
        
        response = requests.post(
            'http://localhost:8000/api/add-expense',
            params={'date': 'invalid', 'merchant': 'Test', 'category': 'food', 'amount': -5}
        )
        
        self.assertEqual(response.status_code, 422)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
import requests
import pytest

@pytest.fixture
def api_client():
    return requests.Session()

class TestFinSightAPIIntegration:
    
    def test_full_workflow(self, api_client):
        """Test complete workflow"""
        base_url = 'http://localhost:8000/api'
        
        # 1. Add expense
        response = api_client.post(
            f'{base_url}/add-expense',
            params={
                'date': '2024-03-13',
                'merchant': 'Starbucks',
                'category': 'food',
                'amount': 6.50
            }
        )
        assert response.status_code == 201
        
        # 2. Get spending summary
        response = api_client.get(
            f'{base_url}/spending-summary',
            params={'days': 30}
        )
        assert response.status_code == 200
        assert 'summary' in response.json()
        
        # 3. Get monthly insights
        response = api_client.get(
            f'{base_url}/monthly-insights',
            params={'months': 3}
        )
        assert response.status_code == 200
        assert 'trends' in response.json()
```

---

## Monitoring & Logging

### API Performance Monitoring

```python
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIMonitor:
    def __init__(self):
        self.request_times = []
        self.error_count = 0
        self.success_count = 0
    
    def log_request(self, endpoint: str, method: str, duration: float, status: int):
        """Log API request"""
        self.request_times.append(duration)
        
        if 200 <= status < 300:
            self.success_count += 1
        else:
            self.error_count += 1
        
        logger.info(
            f"{method} {endpoint}: {status} ({duration:.2f}s)"
        )
    
    def get_stats(self):
        """Get performance statistics"""
        if not self.request_times:
            return {}
        
        return {
            'avg_response_time': sum(self.request_times) / len(self.request_times),
            'max_response_time': max(self.request_times),
            'min_response_time': min(self.request_times),
            'success_count': self.success_count,
            'error_count': self.error_count,
            'error_rate': self.error_count / (self.success_count + self.error_count)
        }

# Usage
monitor = APIMonitor()

start = time.time()
response = requests.get('http://localhost:8000/api/spending-summary')
duration = time.time() - start

monitor.log_request('/spending-summary', 'GET', duration, response.status_code)
print(monitor.get_stats())
```

---

## Deployment Considerations

### Environment Configuration

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '10'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    CACHE_TTL = int(os.getenv('CACHE_TTL', '300'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# .env file
API_BASE_URL=https://api.finsight.com
API_TIMEOUT=30
MAX_RETRIES=5
CACHE_TTL=600
LOG_LEVEL=DEBUG
```

---

## Next Steps

1. ✅ Review integration patterns
2. ✅ Implement error handling strategy
3. ✅ Set up caching and performance optimization
4. ✅ Implement security validations
5. ✅ Write comprehensive tests
6. ✅ Monitor API performance
7. ✅ Deploy to staging environment
8. ✅ Perform load testing
9. ✅ Deploy to production

---

**Version:** 1.0.0  
**Last Updated:** March 2024
