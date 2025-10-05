# AMAS - Advanced Multi-Agent Intelligence System
# Professional Makefile for Development and Operations

.PHONY: help install install-dev test lint format clean setup run build deploy

# Default target
help: ## Show this help message
	@echo "AMAS - Advanced Multi-Agent Intelligence System"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e .[dev]

# Development
setup: ## Setup development environment
	python -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && make install-dev
	. venv/bin/activate && pre-commit install

# Code Quality
lint: ## Run linting checks
	flake8 src/ tests/
	mypy src/
	bandit -r src/

format: ## Format code
	black src/ tests/
	isort src/ tests/

# Testing
test: ## Run tests
	pytest tests/ -v --cov=src/amas --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v

test-e2e: ## Run end-to-end tests only
	pytest tests/e2e/ -v

# Application
run: ## Run the application
	python main.py

run-api: ## Run the API server
	cd src && python -m uvicorn amas.api.main:app --reload --host 0.0.0.0 --port 8000

run-cli: ## Run the CLI interface
	python -m amas.cli

# Docker
build: ## Build Docker image
	docker build -t amas:latest .

run-docker: ## Run with Docker Compose
	docker-compose up -d

stop-docker: ## Stop Docker Compose services
	docker-compose down

# Database
init-db: ## Initialize database
	python scripts/setup_database.py

migrate: ## Run database migrations
	cd src && python -m alembic upgrade head

# Security
security-check: ## Run security checks
	bandit -r src/
	safety check

# Documentation
docs: ## Generate documentation
	cd docs && sphinx-build -b html . _build/html

# Cleanup
clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/

clean-logs: ## Clean log files
	rm -rf logs/*.log

# Development Workflow
dev-setup: clean setup ## Complete development setup
	@echo "Development environment setup complete!"
	@echo "Run 'make run' to start the application"

ci: lint test security-check ## Run CI pipeline locally

# Production
deploy: ## Deploy to production
	@echo "Deploying AMAS to production..."
	docker-compose -f docker-compose.yml up -d

# Monitoring
status: ## Check system status
	curl -s http://localhost:8000/health | jq .

logs: ## View application logs
	docker-compose logs -f amas-api

# Quick Start
quick-start: setup run ## Quick start for new developers
	@echo "AMAS is starting up..."