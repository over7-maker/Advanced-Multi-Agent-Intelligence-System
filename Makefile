# AMAS Project Makefile
# Provides easy commands for development and maintenance

.PHONY: help install test format lint fix clean

# Default target
help:
	@echo "🤖 AMAS Project Commands"
	@echo "========================"
	@echo ""
	@echo "📦 Setup:"
	@echo "  install     Install dependencies"
	@echo "  setup       Setup development environment"
	@echo ""
	@echo "🔧 Code Quality:"
	@echo "  format      Format code with Black and isort"
	@echo "  lint        Run linting checks"
	@echo "  fix         Auto-fix code quality issues"
	@echo "  check       Run all quality checks"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test        Run tests"
	@echo "  test-cov    Run tests with coverage"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean       Clean up temporary files"
	@echo "  clean-all   Clean up all generated files"

# Setup commands
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install black isort flake8 mypy pre-commit

setup: install
	@echo "🔧 Setting up development environment..."
	pre-commit install
	@echo "✅ Development environment ready!"

# Code quality commands
format:
	@echo "🎨 Formatting code..."
	python3 -m black src/ tests/
	python3 -m isort src/ tests/
	@echo "✅ Code formatted!"

lint:
	@echo "🔍 Running linting checks..."
	python3 -m flake8 src/ tests/ --max-complexity=10 --max-line-length=100
	@echo "✅ Linting completed!"

fix:
	@echo "🤖 Auto-fixing code quality issues..."
	./.github/scripts/simple-auto-fix.sh
	@echo "✅ Auto-fix completed!"

check: format lint
	@echo "✅ All quality checks passed!"

# Testing commands
test:
	@echo "🧪 Running tests..."
	python3 -m pytest tests/ -v
	@echo "✅ Tests completed!"

test-cov:
	@echo "🧪 Running tests with coverage..."
	python3 -m pytest tests/ --cov=src/ --cov-report=html
	@echo "✅ Tests with coverage completed!"

# Maintenance commands
clean:
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "✅ Cleanup completed!"

clean-all: clean
	@echo "🧹 Cleaning up all generated files..."
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -rf dist/ build/
	@echo "✅ Full cleanup completed!"

# Quick development workflow
dev: fix test
	@echo "🚀 Development workflow completed!"

# CI simulation
ci: install fix check test
	@echo "🏗️ CI workflow completed!"