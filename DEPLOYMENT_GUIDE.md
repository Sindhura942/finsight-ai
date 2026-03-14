# Production Deployment Guide

**FinSight AI - Deployment & Operations**  
**Version:** 1.0.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Environment Setup](#environment-setup)
4. [Deployment Strategies](#deployment-strategies)
5. [Monitoring & Logging](#monitoring--logging)
6. [Scaling & Performance](#scaling--performance)
7. [Security Hardening](#security-hardening)
8. [Disaster Recovery](#disaster-recovery)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

Production deployment requires careful planning to ensure:

✅ **Reliability** - System stays up and responsive  
✅ **Security** - Data and API protected  
✅ **Performance** - Response times optimized  
✅ **Monitoring** - Issues detected early  
✅ **Scalability** - Handle growth  
✅ **Recoverability** - Data backup and restore  

### Deployment Architecture

```
┌─────────────────────────────────────────┐
│   CloudFront / CDN                      │
│   (Static assets, caching)              │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│   Load Balancer (ALB/NLB)               │
│   (SSL/TLS termination, routing)        │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
    ┌───▼──┐  ┌───▼──┐  ┌───▼──┐
    │ App  │  │ App  │  │ App  │
    │ Pod1 │  │ Pod2 │  │ Pod3 │
    └───┬──┘  └───┬──┘  └───┬──┘
        │         │         │
        └─────────┼─────────┘
                  │
       ┌──────────▼──────────┐
       │   PostgreSQL (RDS)  │
       │   (Primary/Replica) │
       └─────────────────────┘
                  │
       ┌──────────▼──────────┐
       │   Redis Cache       │
       │   (Session/Cache)   │
       └─────────────────────┘
                  │
       ┌──────────▼──────────┐
       │   S3 Bucket         │
       │   (Receipts, files) │
       └─────────────────────┘
```

---

## ✅ Pre-Deployment Checklist

### Code Quality

- [ ] All tests passing (unit, integration, E2E)
- [ ] Code coverage >90%
- [ ] No security vulnerabilities (OWASP)
- [ ] No hardcoded secrets/passwords
- [ ] Linting passing (flake8, black)
- [ ] Type checking passing (mypy)
- [ ] Documentation complete
- [ ] API documentation (Swagger) updated

### Infrastructure

- [ ] Database schema migrations prepared
- [ ] Database backups configured
- [ ] SSL/TLS certificates ready
- [ ] DNS configured
- [ ] CDN configured
- [ ] Monitoring setup complete
- [ ] Alerting rules configured
- [ ] Load balancer configured

### Configuration

- [ ] Environment variables defined
- [ ] Configuration files for prod
- [ ] Secret management (AWS Secrets Manager)
- [ ] API keys configured
- [ ] CORS origins configured
- [ ] Rate limiting configured
- [ ] Logging level set
- [ ] Database connection pooling configured

### Security

- [ ] Authentication working (JWT tokens)
- [ ] Authorization working (role-based)
- [ ] Input validation comprehensive
- [ ] SQL injection prevented
- [ ] XSS protection enabled
- [ ] CSRF protection enabled
- [ ] Rate limiting enabled
- [ ] HTTPS only enforced

### Operations

- [ ] Deployment script tested
- [ ] Rollback procedure documented
- [ ] Incident response plan
- [ ] On-call schedule established
- [ ] Communication channels setup
- [ ] Runbooks prepared

---

## 🔧 Environment Setup

### Production Environment Variables

Create `.env.production`:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_DEBUG=false
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Database
DATABASE_URL=postgresql://user:${DB_PASSWORD}@prod-db.amazonaws.com:5432/finsight
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
DATABASE_ECHO=false

# Redis Cache
REDIS_URL=redis://prod-redis.amazonaws.com:6379/0
CACHE_TTL=300

# Security
SECRET_KEY=${PROD_SECRET_KEY}
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_HOSTS=finsight.com,www.finsight.com,api.finsight.com

# External Services
OCR_SERVICE_URL=https://ocr-prod.service.com
OCR_SERVICE_TIMEOUT=30
OCR_SERVICE_API_KEY=${OCR_API_KEY}

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_KEY}
S3_BUCKET=finsight-prod-receipts

# Features
ENABLE_OCR=true
ENABLE_AI_INSIGHTS=true
ENABLE_BUDGET_ALERTS=true

# CORS
CORS_ORIGINS=https://finsight.com,https://www.finsight.com

# Monitoring
SENTRY_DSN=${SENTRY_DSN}
DATADOG_API_KEY=${DATADOG_API_KEY}
```

### Using AWS Secrets Manager

```python
# app/core/config.py

import json
import boto3
from functools import lru_cache

def get_secrets(secret_name):
    """Get secrets from AWS Secrets Manager."""
    client = boto3.client('secretsmanager')
    
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        logger.error(f"Failed to retrieve secrets: {e}")
        raise

@lru_cache
def get_settings():
    """Get settings with secrets."""
    secrets = get_secrets("finsight/prod")
    return Settings(
        secret_key=secrets['secret_key'],
        database_url=secrets['database_url'],
        # ... other settings
    )
```

### Docker Setup

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY streamlit_app.py .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose (Local & Staging)

```yaml
# docker-compose.yml

version: '3.8'

services:
  # FastAPI Backend
  api:
    build: .
    container_name: finsight-api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://finsight:password@db:5432/finsight
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app/backend
    command: uvicorn backend.main:app --host 0.0.0.0 --reload
  
  # PostgreSQL Database
  db:
    image: postgres:15
    container_name: finsight-db
    environment:
      - POSTGRES_USER=finsight
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=finsight
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U finsight"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  # Redis Cache
  redis:
    image: redis:7
    container_name: finsight-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
  
  # Streamlit Dashboard
  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    container_name: finsight-dashboard
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api

volumes:
  postgres_data:
```

---

## 🚀 Deployment Strategies

### Blue-Green Deployment

```bash
#!/bin/bash
# deploy.sh - Blue-Green deployment

set -e

ENVIRONMENT=$1
BLUE_CLUSTER="finsight-blue"
GREEN_CLUSTER="finsight-green"
LOAD_BALANCER="finsight-lb"

# Get current active cluster
CURRENT=$(aws elbv2 describe-target-groups \
  --load-balancer-arn $LOAD_BALANCER \
  --query 'TargetGroups[0].TargetGroupName' \
  --output text)

if [ "$CURRENT" == "$BLUE_CLUSTER" ]; then
    ACTIVE=$BLUE_CLUSTER
    STANDBY=$GREEN_CLUSTER
else
    ACTIVE=$GREEN_CLUSTER
    STANDBY=$BLUE_CLUSTER
fi

echo "Active: $ACTIVE, Deploying to: $STANDBY"

# 1. Deploy to standby cluster
echo "Deploying to $STANDBY..."
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d --build

# 2. Run health checks
echo "Running health checks..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health; then
        echo "Health check passed"
        break
    fi
    echo "Waiting for service... ($i/30)"
    sleep 2
done

# 3. Run smoke tests
echo "Running smoke tests..."
pytest tests/smoke/ -v

# 4. Switch traffic
echo "Switching traffic to $STANDBY..."
aws elbv2 modify-rule \
  --rule-arn $STANDBY \
  --actions Type=forward,TargetGroupArn=$STANDBY

# 5. Monitor
echo "Monitoring for 5 minutes..."
sleep 300

# Check error rate
ERROR_RATE=$(aws cloudwatch get-metric-statistics \
  --metric-name HTTPServerErrors \
  --namespace AWS/ApplicationELB \
  --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --query 'Datapoints[0].Average' \
  --output text)

if (( $(echo "$ERROR_RATE > 1" | bc -l) )); then
    echo "Error rate high! Rolling back..."
    # Switch back to active
    aws elbv2 modify-rule \
      --rule-arn $ACTIVE \
      --actions Type=forward,TargetGroupArn=$ACTIVE
    exit 1
fi

echo "Deployment successful!"
```

### Rolling Deployment

```bash
#!/bin/bash
# rolling-deploy.sh - Rolling deployment

CLUSTER="finsight-prod"
SERVICE="finsight-api"
NEW_VERSION=$1

echo "Deploying $SERVICE v$NEW_VERSION"

# Update ECS task definition
aws ecs register-task-definition \
  --family $SERVICE \
  --container-definitions file://task-definition.json \
  --query 'taskDefinition.taskDefinitionArn' \
  --output text

# Update service with new task definition
aws ecs update-service \
  --cluster $CLUSTER \
  --service $SERVICE \
  --force-new-deployment

# Wait for deployment
aws ecs wait services-stable \
  --cluster $CLUSTER \
  --services $SERVICE

echo "Deployment completed successfully"
```

### Canary Deployment

```bash
#!/bin/bash
# canary-deploy.sh - Canary deployment

SERVICE="finsight-api"
CANARY_PERCENTAGE=10  # Start with 10% traffic

# Deploy new version
NEW_VERSION=$1

# Set canary weight (10% new, 90% old)
aws appconfig create-deployment \
  --application-id $SERVICE \
  --environment-id prod \
  --deployment-strategy-id "Canary($CANARY_PERCENTAGE)" \
  --configuration-name "version" \
  --configuration-version "$NEW_VERSION"

# Monitor metrics
for i in {1..10}; do
    echo "Checking canary metrics... ($i/10)"
    
    # Get error rate for canary
    ERROR_RATE=$(aws cloudwatch get-metric-statistics \
      --metric-name HTTPServerErrors \
      --dimensions Name=CanaryGroup,Value=new \
      --start-time $(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S) \
      --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
      --period 300 \
      --statistics Average)
    
    if [ "$ERROR_RATE" -gt "5" ]; then
        echo "Canary failed! Rolling back..."
        aws appconfig stop-deployment --deployment-id $DEPLOYMENT_ID
        exit 1
    fi
    
    sleep 30
done

# Increase to 50%
echo "Increasing to 50% traffic..."
aws appconfig update-deployment \
  --deployment-strategy-id "Canary(50)"

# Final check
echo "Increasing to 100% traffic..."
aws appconfig update-deployment \
  --deployment-strategy-id "Linear(100%)"

echo "Canary deployment successful!"
```

---

## 📊 Monitoring & Logging

### Structured Logging Setup

```python
# app/core/logger.py

import json
import logging
from pythonjsonlogger import jsonlogger
from pythonjsonlogger.formatters import JSONFormatter

def setup_logging(log_level="INFO"):
    """Setup JSON logging for production."""
    
    # Create logger
    logger = logging.getLogger("finsight")
    logger.setLevel(log_level)
    
    # JSON formatter
    formatter = JSONFormatter(
        fmt="%(timestamp)s %(name)s %(levelname)s %(message)s",
        timestamp=True,
    )
    
    # Console handler (for container logs)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
```

### CloudWatch Integration

```python
# app/core/monitoring.py

import watchtower
import logging

def setup_cloudwatch(log_group="/finsight/api/prod"):
    """Setup CloudWatch logging."""
    
    cloudwatch_handler = watchtower.CloudWatchLogHandler(
        log_group=log_group,
        stream_name="api-logs",
        use_queues=True,  # Async logging
    )
    
    logger = logging.getLogger("finsight")
    logger.addHandler(cloudwatch_handler)
    
    return logger
```

### Application Performance Monitoring (APM)

```python
# app/core/apm.py

from elastic_apm import Client

# Elastic APM
apm_client = Client(
    service_name="finsight-api",
    environment="production",
    server_url="https://apm.elastic.co",
)

# Sentry Error Tracking
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    environment="production",
    traces_sample_rate=0.1,  # 10% sampling
    integrations=[
        sentry_sdk.integrations.fastapi.FastApiIntegration(),
        sentry_sdk.integrations.sqlalchemy.SqlalchemyIntegration(),
    ],
)
```

### Monitoring Dashboards

```yaml
# monitoring/dashboards.yml

Dashboards:
  API_Health:
    Metrics:
      - Request_Count (5min)
      - Response_Time_P50, P95, P99
      - Error_Rate (HTTP 5xx)
      - Database_Connection_Pool_Usage
      - Cache_Hit_Rate
      - Redis_Memory_Usage
    
  Database:
    Metrics:
      - Active_Connections
      - Query_Duration_P99
      - Replication_Lag
      - Disk_Usage
      - Transaction_Rate
    
  Infrastructure:
    Metrics:
      - CPU_Usage
      - Memory_Usage
      - Disk_Usage
      - Network_In/Out
      - Container_Count
```

---

## 🔒 Security Hardening

### Security Headers

```python
# app/middleware/security.py

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
```

### Rate Limiting

```python
# app/middleware/rate_limit.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Apply to routes
@app.get("/api/expenses")
@limiter.limit("60/minute")
async def get_expenses(request: Request):
    pass
```

### SQL Injection Prevention

```python
# Using ORM prevents SQL injection
from sqlalchemy import select

# Safe - uses parameterized queries
expenses = db.query(Expense).filter(
    Expense.merchant == merchant_name
).all()

# Never use string concatenation
# BAD: f"SELECT * FROM expenses WHERE merchant = '{merchant}'"
```

### HTTPS Enforcement

```python
# app/middleware/https.py

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.scheme == "http":
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=url)
        
        return await call_next(request)
```

---

## 🔄 Scaling & Performance

### Horizontal Scaling

```yaml
# kubernetes-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: finsight-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: finsight-api
  template:
    metadata:
      labels:
        app: finsight-api
    spec:
      containers:
      - name: api
        image: finsight-api:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

### Database Connection Pooling

```python
# app/database/session.py

from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to keep
    max_overflow=10,  # Additional connections when pool exhausted
    pool_pre_ping=True,  # Verify connections before use
    echo=False,
)
```

### Caching Strategy

```python
# Cache frequently accessed data
@app.get("/api/expenses/summary")
@cache(expire=300)  # Cache for 5 minutes
async def get_summary():
    return calculate_summary()

# Cache expensive calculations
def get_category_breakdown():
    # Check Redis first
    cached = redis.get("category_breakdown")
    if cached:
        return json.loads(cached)
    
    # Calculate
    breakdown = expensive_calculation()
    
    # Cache for 1 hour
    redis.setex("category_breakdown", 3600, json.dumps(breakdown))
    
    return breakdown
```

### Database Optimization

```python
# Use indexes for frequently queried columns
class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant = Column(String(255), index=True)  # Index for filtering
    category = Column(String(50), index=True)   # Index for filtering
    date = Column(DateTime, index=True)         # Index for date range queries
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Composite index for common queries
    __table_args__ = (
        Index("idx_user_date", "user_id", "date"),
    )

# Query optimization with joins
expenses = db.query(Expense).options(
    joinedload(Expense.receipts),  # Eager load related receipts
    joinedload(Expense.user),       # Eager load user
).filter(Expense.user_id == user_id).all()
```

---

## 🆘 Disaster Recovery

### Database Backup

```bash
#!/bin/bash
# backup-database.sh

DB_NAME="finsight"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
pg_dump -h prod-db.amazonaws.com \
  -U finsight \
  -d $DB_NAME > $BACKUP_DIR/finsight_$DATE.sql

# Compress
gzip $BACKUP_DIR/finsight_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/finsight_$DATE.sql.gz \
  s3://finsight-backups/daily/

# Keep only last 30 days
find $BACKUP_DIR -name "finsight_*.sql.gz" -mtime +30 -delete

echo "Backup completed: finsight_$DATE.sql.gz"
```

### Automated Backups (AWS RDS)

```python
# Enable automated backups in RDS
import boto3

rds = boto3.client('rds')

rds.modify_db_instance(
    DBInstanceIdentifier='finsight-prod',
    BackupRetentionPeriod=30,  # Keep 30 days of backups
    PreferredBackupWindow='03:00-04:00',  # 3 AM UTC
    EnableCloudwatchLogsExports=['postgresql'],
)
```

### Database Restore Procedure

```bash
#!/bin/bash
# restore-database.sh

BACKUP_FILE=$1  # e.g., finsight_20240313_150000.sql.gz

# Download from S3
aws s3 cp s3://finsight-backups/daily/$BACKUP_FILE .

# Decompress
gunzip $BACKUP_FILE
BACKUP_SQL="${BACKUP_FILE%.gz}"

# Restore to database
psql -h prod-db.amazonaws.com \
  -U finsight \
  -d finsight < $BACKUP_SQL

echo "Database restored from $BACKUP_FILE"
```

### Replication & Failover

```python
# AWS RDS Multi-AZ
import boto3

rds = boto3.client('rds')

rds.modify_db_instance(
    DBInstanceIdentifier='finsight-prod',
    MultiAZ=True,  # Enable Multi-AZ deployment
    ApplyImmediately=True,
)

# Automatic failover happens in <2 minutes
# Read replica can be promoted to primary
rds.promote_read_replica(
    DBInstanceIdentifier='finsight-replica',
)
```

---

## 🔍 Troubleshooting

### Common Issues & Solutions

#### Issue: High CPU Usage

```bash
# 1. Check running processes
docker ps

# 2. Check application logs
tail -f logs/application.log | grep ERROR

# 3. Profile CPU usage
python -m cProfile -s cumtime backend/main.py

# 4. Check database queries
SELECT query, calls, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### Issue: Database Connection Pool Exhausted

```python
# Solution: Increase pool size
engine = create_engine(
    DATABASE_URL,
    pool_size=40,  # Increased from 20
    max_overflow=20,  # Increased from 10
)

# Solution: Use connection pooling middleware
from sqlalchemy.pool import NullPool  # Don't pool connections
# Or implement better connection management
```

#### Issue: Memory Leak

```bash
# Check memory usage over time
docker stats finsight-api

# Profile memory
python -m memory_profiler backend/main.py

# Check for circular references
import gc
gc.collect()
unreachable = gc.garbage
```

#### Issue: Slow API Responses

```python
# 1. Add timing to logs
import time
start = time.time()
result = expensive_operation()
duration = time.time() - start
logger.info(f"Operation took {duration}s")

# 2. Use caching
@cache(expire=600)
async def get_summary():
    return calculate_summary()

# 3. Add database indexes
# 4. Use query optimization
# 5. Enable gzip compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## 📋 Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Security scan passed
- [ ] Performance benchmarks acceptable
- [ ] Database migrations prepared
- [ ] Backups verified
- [ ] DNS updated
- [ ] SSL certificates valid
- [ ] Monitoring configured
- [ ] Alert thresholds set
- [ ] Incident response team ready
- [ ] Communication channels open
- [ ] Deployment window scheduled
- [ ] Rollback procedure documented
- [ ] Post-deployment tests planned

---

**Version:** 1.0.0  
**Status:** Ready for Deployment  
**Last Updated:** March 2024

For support: devops@finsight.com
