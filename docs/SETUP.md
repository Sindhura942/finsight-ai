"""Setup Instructions - FinSight AI"""

## Prerequisites

- **Python:** 3.10 or higher
- **macOS/Linux:** Tesseract OCR
- **System RAM:** Minimum 4GB (Ollama + Llama3 requires ~4GB)

## Step-by-Step Installation

### 1. Clone Repository

```bash
cd ~/Downloads
git clone <repo-url> "FinSight AI"
cd "FinSight AI"
```

### 2. Install System Dependencies

#### macOS
```bash
# Install Tesseract OCR
brew install tesseract

# Install Python (if not already installed)
brew install python@3.10
```

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr python3-pip python3-venv
```

#### Fedora
```bash
sudo dnf install tesseract python3-pip
```

### 3. Install Ollama and Llama3

1. **Download Ollama:** https://ollama.ai
2. **Install:** Follow platform-specific instructions
3. **Pull Llama3:**
   ```bash
   ollama pull llama3
   ```
4. **Start Ollama Service:**
   ```bash
   ollama serve
   ```
   (This will run on http://localhost:11434)

### 4. Setup Backend

#### Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configure Environment
```bash
# Copy example env file
cp ../.env.example ../.env

# Edit .env with your settings (optional)
# nano ../.env
```

#### Initialize Database
```bash
# Database will be created automatically on first run
python -c "from main import app; from app.database.session import engine; from app.database.models import Base; Base.metadata.create_all(bind=engine)"
```

### 5. Setup Frontend

#### Create Virtual Environment (Optional)
```bash
cd ../frontend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install streamlit requests pandas plotly
```

## Running the Application

### Terminal 1: Start Backend API

```bash
cd backend
source venv/bin/activate
python main.py
```

Expected output:
```
Starting FinSight AI v0.1.0
API running on 0.0.0.0:8000
```

Visit: http://localhost:8000/docs (API documentation)

### Terminal 2: Start Ollama (if not already running)

```bash
ollama serve
```

Expected output:
```
Listening on [::]:11434
```

### Terminal 3: Start Frontend

```bash
cd frontend
source venv/bin/activate
streamlit run app.py
```

Expected output:
```
Listening on http://localhost:8501
```

Visit: http://localhost:8501 in your browser

## Verification

### Check Backend Health
```bash
curl http://localhost:8000/api/health/
```

Expected response:
```json
{
  "status": "ok",
  "database": "ok",
  "llm_service": "ok"
}
```

### Check Ollama
```bash
curl http://localhost:11434/api/tags
```

### Test OCR (Optional)
```bash
# Place a test image at /tmp/test_receipt.jpg
cd backend
python -c "
from app.services.ocr_service import OCRService
ocr = OCRService()
text, confidence = ocr.extract_text_from_image('/tmp/test_receipt.jpg')
print(f'Text: {text}')
print(f'Confidence: {confidence}')
"
```

## Running Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

## Code Quality

### Format Code
```bash
black app/ tests/
isort app/ tests/
```

### Lint Code
```bash
flake8 app/ tests/
mypy app/
```

## Troubleshooting

### Ollama Connection Error
```
Error: Failed to connect to Ollama at http://localhost:11434
```
**Solution:** Ensure Ollama is running and accessible
```bash
ollama serve  # In another terminal
```

### Tesseract Not Found
```
Error: tesseract is not installed or it's not in your PATH
```
**Solution:** Install Tesseract:
```bash
# macOS
brew install tesseract

# Linux
sudo apt-get install tesseract-ocr
```

### Database Locked Error
```
Error: database is locked
```
**Solution:** Only one process can write to SQLite at a time
- Ensure you have only one backend instance running
- Check for zombie processes: `ps aux | grep python`

### Out of Memory
```
Error: CUDA out of memory or similar LLM error
```
**Solution:** 
- Ensure you have at least 4GB free RAM
- Consider using a smaller Ollama model or GPU acceleration

### Port Already in Use
```
Error: Address already in use
```
**Solution:** Kill existing process or change port
```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in .env
API_PORT=8001
```

## Production Deployment

For production, consider:

1. **Database:** Upgrade to PostgreSQL for multi-user support
2. **Authentication:** Add JWT/OAuth authentication
3. **Rate Limiting:** Add rate limiting middleware
4. **Caching:** Add Redis for caching
5. **Monitoring:** Add Prometheus/Grafana monitoring
6. **Logging:** Use centralized logging (ELK stack)
7. **API Gateway:** Use Nginx/Apache for reverse proxy
8. **Docker:** Containerize for easy deployment
9. **SSL/TLS:** Enable HTTPS
10. **Secrets Management:** Use environment-based secrets

## Docker Setup (Optional)

```dockerfile
# Dockerfile for Backend
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t finsight-ai-backend .
docker run -p 8000:8000 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 finsight-ai-backend
```

## Next Steps

1. **Upload your first receipt:** Use the Streamlit frontend
2. **Explore analytics:** Check the Dashboard tab
3. **Review recommendations:** See cost-saving suggestions
4. **Customize categories:** Edit `EXPENSE_CATEGORIES` in `app/core/constants.py`
5. **Integrate with your data:** Connect to banking APIs

## Getting Help

- **API Documentation:** http://localhost:8000/docs
- **GitHub Issues:** Report bugs and feature requests
- **Documentation:** See `/docs` directory
