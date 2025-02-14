.PHONY: all setup test lint format check clean install install-dev build publish

# Default target
all: setup lint test

# Setup development environment
setup:
	poetry install --with dev

# Run tests
test:
	poetry run pytest tests/ -v

# Run all linting and type checking
lint: format-check lint-check type-check

# Format code
format:
	poetry run black .
	poetry run isort .

# Check formatting
format-check:
	poetry run black --check .
	poetry run isort --check .

# Run linting
lint-check:
	poetry run ruff check .

# Run type checking
type-check:
	poetry run mypy src/

# Clean up
clean:
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build package
build: clean
	poetry build

# Install package locally
install:
	poetry install

# Install development dependencies
install-dev:
	poetry install --with dev

# Export requirements
requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes
	poetry export -f requirements.txt --output requirements-dev.txt --with dev --without-hashes

# Run the server
run:
	poetry run python -m mockllm

# Help target
help:
	@echo "Available targets:"
	@echo "  all          : Run setup, lint, and test"
	@echo "  setup        : Set up development environment with Poetry"
	@echo "  test         : Run tests"
	@echo "  lint         : Run all code quality checks"
	@echo "  format       : Format code with black and isort"
	@echo "  format-check : Check code formatting"
	@echo "  lint-check   : Run ruff linter"
	@echo "  type-check   : Run mypy type checker"
	@echo "  clean        : Clean up build artifacts"
	@echo "  build        : Build package"
	@echo "  install      : Install package with Poetry"
	@echo "  install-dev  : Install package with development dependencies"
	@echo "  requirements : Export requirements.txt files"
	@echo "  run          : Run the server"