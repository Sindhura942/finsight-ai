#!/bin/bash

# FinSight AI Quick Start Script
# This script helps you set up and run FinSight AI

set -e

echo "🚀 FinSight AI Quick Start"
echo "=========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create backend virtual environment
echo ""
echo -e "${YELLOW}Setting up backend...${NC}"
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓ Backend setup complete${NC}"

# Create frontend virtual environment
echo ""
echo -e "${YELLOW}Setting up frontend...${NC}"
cd ../frontend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓ Frontend setup complete${NC}"

# Check system dependencies
echo ""
echo -e "${YELLOW}Checking system dependencies...${NC}"

# Check Tesseract
if ! command -v tesseract &> /dev/null; then
    echo -e "${RED}✗ Tesseract not found${NC}"
    echo "  Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)"
else
    echo -e "${GREEN}✓ Tesseract found${NC}"
fi

# Check Ollama
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠ Ollama not running${NC}"
    echo "  Start Ollama with: ollama serve"
else
    echo -e "${GREEN}✓ Ollama is running${NC}"
fi

# Print startup instructions
echo ""
echo -e "${GREEN}Setup complete! Here's how to start:${NC}"
echo ""
echo "1. In Terminal 1 - Start Ollama (if not already running):"
echo "   ${YELLOW}ollama serve${NC}"
echo ""
echo "2. In Terminal 2 - Start Backend:"
echo "   ${YELLOW}cd backend && source venv/bin/activate && python main.py${NC}"
echo ""
echo "3. In Terminal 3 - Start Frontend:"
echo "   ${YELLOW}cd frontend && source venv/bin/activate && streamlit run app.py${NC}"
echo ""
echo "Then open:"
echo "   - API: ${YELLOW}http://localhost:8000/docs${NC}"
echo "   - Dashboard: ${YELLOW}http://localhost:8501${NC}"
echo ""
