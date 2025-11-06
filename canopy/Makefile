.PHONY: help install test test-watch test-cov format lint clean all

# Default target
help:
	@echo "Canopy Trading Language - Development Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install       - Install dependencies with Poetry"
	@echo "  make test          - Run all tests with pytest"
	@echo "  make test-watch    - Run tests in watch mode (TDD)"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make format        - Format code with black and isort"
	@echo "  make lint          - Run linters (flake8 + mypy)"
	@echo "  make clean         - Remove build artifacts and cache"
	@echo "  make all           - Run format, lint, and test"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies with Poetry..."
	poetry install
	@echo "Done! Run 'poetry shell' to activate the virtual environment."

# Run tests
test:
	@echo "Running tests..."
	poetry run pytest

# Run tests in watch mode for TDD
test-watch:
	@echo "Running tests in watch mode (TDD)..."
	@echo "Press Ctrl+C to stop"
	poetry run ptw -- -v

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	poetry run pytest --cov=src/canopy --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

# Format code
format:
	@echo "Formatting code with black..."
	poetry run black src/ tests/
	@echo "Sorting imports with isort..."
	poetry run isort src/ tests/
	@echo "Code formatting complete!"

# Run linters
lint:
	@echo "Running flake8..."
	poetry run flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	@echo "Running mypy..."
	poetry run mypy src/
	@echo "Linting complete!"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"

# Run all checks (format, lint, test)
all: format lint test
	@echo "All checks passed!"
