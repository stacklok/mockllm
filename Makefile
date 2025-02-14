.PHONY: all setup test lint format check clean

# Default target
all: setup lint test

# Setup development environment
setup:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v

# Run all linting and type checking
lint: format-check lint-check type-check

# Format code
format:
	black .
	isort .

# Check formatting
format-check:
	black --check .
	isort --check .

# Run linting
lint-check:
	ruff check .

# Run type checking
type-check:
	mypy src/

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	python -m build

# Install package locally
install:
	pip install -e .

# Install development dependencies
install-dev:
	pip install -e ".[dev]"

# Help target
help:
	@echo "Available targets:"
	@echo "  all          : Run setup, lint, and test"
	@echo "  setup        : Set up development environment"
	@echo "  test         : Run tests"
	@echo "  lint         : Run all code quality checks"
	@echo "  format       : Format code with black and isort"
	@echo "  format-check : Check code formatting"
	@echo "  lint-check   : Run ruff linter"
	@echo "  type-check   : Run mypy type checker"
	@echo "  clean        : Clean up build artifacts"
	@echo "  build        : Build package"
	@echo "  install      : Install package locally"
	@echo "  install-dev  : Install package with development dependencies"