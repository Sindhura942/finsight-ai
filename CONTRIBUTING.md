"""Contributing to FinSight AI"""

## How to Contribute

We welcome contributions to FinSight AI! Here's how you can help:

### Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup

```bash
# Install dependencies
pip install -r backend/requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest backend/tests/ -v

# Format code
black app/ tests/
isort app/ tests/

# Check code quality
flake8 app/ tests/
mypy app/
```

### Code Style

- Use **Black** for code formatting
- Use **isort** for import sorting
- Follow **PEP 8** standards
- Write docstrings for all functions and classes
- Use type hints where possible

### Testing

- Write tests for new features
- Maintain test coverage above 80%
- Run tests before submitting PR: `pytest tests/ -v --cov`

### Commit Messages

Use clear, descriptive commit messages:
- `feat: Add new feature`
- `fix: Fix bug in module`
- `docs: Update documentation`
- `test: Add test for feature`
- `refactor: Refactor module`
- `style: Format code`

### Pull Request Process

1. Update documentation if needed
2. Add/update tests
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Submit PR with clear description
6. Respond to code review feedback

### Reporting Issues

Report bugs using GitHub Issues. Include:
- Clear description
- Steps to reproduce
- Expected behavior
- Actual behavior
- Python version
- OS/Platform

### Feature Requests

Suggest improvements using GitHub Issues with:
- Clear description
- Use cases
- Proposed implementation (optional)

## Project Structure

```
FinSight AI/
├── backend/          # FastAPI backend
├── frontend/         # Streamlit frontend
├── docs/             # Documentation
└── tests/            # Test files
```

## Architecture Guidelines

- **Services:** Business logic layer
- **API:** REST endpoint handlers
- **Database:** Data access and ORM models
- **Models:** Pydantic schemas and validation
- **Core:** Configuration and utilities

## Areas for Contribution

- **Features:** New analysis types, visualizations
- **Integrations:** Bank API, payment platform integrations
- **Frontend:** Enhanced UI/UX, new pages
- **Backend:** Performance improvements, caching
- **Testing:** More comprehensive tests
- **Documentation:** Guides, examples, tutorials
- **DevOps:** Docker, CI/CD, deployment configs

## Questions?

Open a discussion or issue on GitHub.

Thank you for contributing to FinSight AI! 🙏
