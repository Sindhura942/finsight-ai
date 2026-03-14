"""
FinSight AI - Build and Development Tasks
"""

# Task definitions for common development activities

[build]
# Build commands
backend-install = "cd backend && pip install -r requirements.txt"
frontend-install = "cd frontend && pip install -r requirements.txt"
dev-install = "pip install -r requirements-dev.txt"

[run]
# Run commands
backend = "cd backend && python main.py"
frontend = "cd frontend && streamlit run app.py"
ollama = "ollama serve"

[test]
# Test commands
unit-tests = "cd backend && pytest tests/ -v"
unit-tests-cov = "cd backend && pytest tests/ -v --cov=app"
integration-tests = "cd backend && pytest tests/ -v -m integration"

[quality]
# Code quality commands
format = "black app/ tests/ && isort app/ tests/"
lint = "flake8 app/ tests/"
type-check = "mypy app/"
test-all = "pytest tests/ && black --check app/ tests/ && flake8 app/ tests/"
