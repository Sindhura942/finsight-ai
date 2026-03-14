@echo off
REM FinSight AI Quick Start Script for Windows

echo.
echo 🚀 FinSight AI Quick Start
echo ==========================
echo.

REM Check Python version
echo Checking Python version...
python --version

REM Setup backend
echo.
echo Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo ✓ Backend setup complete

REM Setup frontend
echo.
echo Setting up frontend...
cd ..\frontend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo ✓ Frontend setup complete

echo.
echo Setup complete! Here's how to start:
echo.
echo 1. In PowerShell/CMD 1 - Start Ollama:
echo    ollama serve
echo.
echo 2. In PowerShell/CMD 2 - Start Backend:
echo    cd backend
echo    venv\Scripts\activate.bat
echo    python main.py
echo.
echo 3. In PowerShell/CMD 3 - Start Frontend:
echo    cd frontend
echo    venv\Scripts\activate.bat
echo    streamlit run app.py
echo.
echo Then open:
echo    - API: http://localhost:8000/docs
echo    - Dashboard: http://localhost:8501
echo.
pause
