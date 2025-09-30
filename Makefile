# AMAS - Advanced Multi-Agent Intelligence System
# Professional Makefile for development and deployment

# =============================================================================
# CONFIGURATION
# =============================================================================

SHELL := /bin/bash
PYTHON := python3
PIP := pip
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
MYPY := mypy
DOCKER := docker
DOCKER_COMPOSE := docker-compose

# Project settings
PROJECT_NAME := amas
SRC_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs

# Docker settings
DOCKER_IMAGE := amas:latest
DOCKER_REGISTRY := your-registry.com
COMPOSE_FILE := docker-compose.yml
COMPOSE_FILE_DEV := docker-compose.dev.yml

# =============================================================================
# HELP
# =============================================================================

.PHONY: help
help: ## Show this help message
	@echo "AMAS - Advanced Multi-Agent Intelligence System"
	@echo "================================================"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# DEVELOPMENT
# =============================================================================

.PHONY: install
install: ## Install development dependencies
	$(PIP) install -e .[dev]
	pre-commit install

.PHONY: install-gpu
install-gpu: ## Install with GPU support
	$(PIP) install -e .[dev,gpu]
	pre-commit install

.PHONY: setup
setup: install ## Complete development setup
	mkdir -p logs data models
	cp .env.example .env
	@echo "✅ Development environment setup complete"
	@echo "📝 Please edit .env file with your configuration"

.PHONY: run
run: ## Run AMAS locally
	$(PYTHON) main.py

.PHONY: dev
dev: ## Run AMAS in development mode with auto-reload
	uvicorn amas.api.main:app --host 0.0.0.0 --port 8000 --reload --app-dir src

.PHONY: shell
shell: ## Start Python shell with AMAS loaded
	$(PYTHON) -c "import sys; sys.path.insert(0, 'src'); from amas import *; print('AMAS development shell ready')"

# =============================================================================
# CODE QUALITY
# =============================================================================

.PHONY: format
format: ## Format code with black and isort
	$(BLACK) $(SRC_DIR) $(TESTS_DIR)
	isort $(SRC_DIR) $(TESTS_DIR)

.PHONY: lint
lint: ## Run linting checks
	$(FLAKE8) $(SRC_DIR) $(TESTS_DIR)
	$(BLACK) --check $(SRC_DIR) $(TESTS_DIR)
	isort --check-only $(SRC_DIR) $(TESTS_DIR)

.PHONY: typecheck
typecheck: ## Run type checking
	$(MYPY) $(SRC_DIR)

.PHONY: security
security: ## Run security checks
	bandit -r $(SRC_DIR)
	safety check
	pip-audit

.PHONY: quality
quality: lint typecheck security ## Run all quality checks

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: ## Run all tests
	$(PYTEST) $(TESTS_DIR)

.PHONY: test-unit
test-unit: ## Run unit tests only
	$(PYTEST) $(TESTS_DIR)/unit

.PHONY: test-integration
test-integration: ## Run integration tests only
	$(PYTEST) $(TESTS_DIR)/integration

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests only
	$(PYTEST) $(TESTS_DIR)/e2e

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	$(PYTEST) --cov=$(PROJECT_NAME) --cov-report=html --cov-report=term-missing

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	$(PYTEST) -f $(TESTS_DIR)

# =============================================================================
# DOCKER
# =============================================================================

.PHONY: docker-build
docker-build: ## Build Docker image
	$(DOCKER) build -t $(DOCKER_IMAGE) -f docker/Dockerfile .

.PHONY: docker-build-dev
docker-build-dev: ## Build development Docker image
	$(DOCKER) build -t $(DOCKER_IMAGE)-dev --target development -f docker/Dockerfile .

.PHONY: docker-run
docker-run: ## Run AMAS in Docker container
	$(DOCKER) run --rm -p 8000:8000 $(DOCKER_IMAGE)

.PHONY: docker-up
docker-up: ## Start all services with Docker Compose
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE) up -d

.PHONY: docker-up-dev
docker-up-dev: ## Start development services with Docker Compose
	$(DOCKER_COMPOSE) -f $(COMPOSE_FILE_DEV) up -d

.PHONY: docker-down
docker-down: ## Stop all Docker Compose services
	$(DOCKER_COMPOSE) down

.PHONY: docker-logs
docker-logs: ## Show Docker Compose logs
	$(DOCKER_COMPOSE) logs -f

.PHONY: docker-clean
docker-clean: ## Clean Docker images and volumes
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER) image prune -f
	$(DOCKER) volume prune -f

# =============================================================================
# DATABASE
# =============================================================================

.PHONY: db-migrate
db-migrate: ## Run database migrations
	alembic upgrade head

.PHONY: db-migration
db-migration: ## Create new database migration
	@read -p "Migration name: " name; \
	alembic revision --autogenerate -m "$$name"

.PHONY: db-reset
db-reset: ## Reset database (WARNING: Destroys data)
	@read -p "Are you sure you want to reset the database? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		alembic downgrade base; \
		alembic upgrade head; \
		echo "Database reset complete"; \
	else \
		echo "Database reset cancelled"; \
	fi

.PHONY: db-seed
db-seed: ## Seed database with sample data
	$(PYTHON) scripts/development/seed_database.py

# =============================================================================
# DOCUMENTATION
# =============================================================================

.PHONY: docs
docs: ## Build documentation
	cd $(DOCS_DIR) && make html

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	cd $(DOCS_DIR) && make html && python -m http.server 8080 -d _build/html

.PHONY: docs-clean
docs-clean: ## Clean documentation build
	cd $(DOCS_DIR) && make clean

# =============================================================================
# MONITORING
# =============================================================================

.PHONY: monitor
monitor: ## Start monitoring stack
	$(DOCKER_COMPOSE) up -d prometheus grafana

.PHONY: logs
logs: ## Show application logs
	tail -f logs/amas.log

.PHONY: status
status: ## Show system status
	$(PYTHON) amas.py status

.PHONY: health
health: ## Perform health check
	$(PYTHON) amas.py health --check-all

# =============================================================================
# DEPLOYMENT
# =============================================================================

.PHONY: build
build: docker-build ## Build production image

.PHONY: deploy-staging
deploy-staging: ## Deploy to staging environment
	@echo "🚀 Deploying to staging..."
	$(DOCKER) tag $(DOCKER_IMAGE) $(DOCKER_REGISTRY)/$(PROJECT_NAME):staging
	$(DOCKER) push $(DOCKER_REGISTRY)/$(PROJECT_NAME):staging
	# Add your staging deployment commands here

.PHONY: deploy-prod
deploy-prod: ## Deploy to production environment
	@echo "🚀 Deploying to production..."
	@read -p "Are you sure you want to deploy to production? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		$(DOCKER) tag $(DOCKER_IMAGE) $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest; \
		$(DOCKER) push $(DOCKER_REGISTRY)/$(PROJECT_NAME):latest; \
		echo "Production deployment complete"; \
	else \
		echo "Production deployment cancelled"; \
	fi

# =============================================================================
# MAINTENANCE
# =============================================================================

.PHONY: backup
backup: ## Create system backup
	$(PYTHON) scripts/maintenance/backup_system.py

.PHONY: update-deps
update-deps: ## Update dependencies
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt

.PHONY: clean
clean: ## Clean build artifacts and cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/

.PHONY: reset
reset: clean docker-clean ## Complete reset (code, Docker, database)
	@read -p "This will reset everything including data. Continue? [y/N] " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		rm -rf logs/* data/* models/*; \
		echo "Complete reset finished"; \
	else \
		echo "Reset cancelled"; \
	fi

# =============================================================================
# CI/CD
# =============================================================================

.PHONY: ci
ci: quality test ## Run CI pipeline locally
	@echo "✅ CI pipeline completed successfully"

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

.PHONY: release
release: ## Create a new release
	@read -p "Release version (current: 1.0.0): " version; \
	if [ -n "$$version" ]; then \
		git tag -a "v$$version" -m "Release v$$version"; \
		git push origin "v$$version"; \
		echo "Release v$$version created"; \
	fi

# =============================================================================
# UTILITIES
# =============================================================================

.PHONY: benchmark
benchmark: ## Run performance benchmarks
	$(PYTHON) scripts/development/benchmark_system.py

.PHONY: profile
profile: ## Profile application performance
	$(PYTHON) -m cProfile -o profile.stats main.py
	$(PYTHON) -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(20)"

.PHONY: check-ports
check-ports: ## Check if required ports are available
	@echo "Checking required ports..."
	@for port in 8000 5432 6379 7474 7687 11434; do \
		if lsof -i :$$port > /dev/null 2>&1; then \
			echo "❌ Port $$port is in use"; \
		else \
			echo "✅ Port $$port is available"; \
		fi; \
	done

.PHONY: init-project
init-project: setup docker-up db-migrate db-seed ## Initialize complete project
	@echo "🎉 AMAS project initialization complete!"
	@echo "🌐 Access the system at: http://localhost:8000"
	@echo "📊 Grafana dashboard: http://localhost:3001"
	@echo "📝 API docs: http://localhost:8000/docs"

# Default target
.DEFAULT_GOAL := help