.PHONY: help build up down restart logs test lint format clean install dev

# Colors
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m

help: ## Show this help
	@echo "$(GREEN)AI-JARVIS Makefile Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# Docker Commands
build: ## Build all containers
	@echo "$(GREEN)Building containers...$(NC)"
	docker-compose build

up: ## Start all services
	@echo "$(GREEN)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Dashboard: http://localhost:3000$(NC)"

down: ## Stop all services
	docker-compose down

restart: down up ## Restart all services

logs: ## View logs
	docker-compose logs -f

ps: ## Show running containers
	docker-compose ps

# Development
dev: ## Start in dev mode
	docker-compose up

install: ## Install dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	cd apps/orchestrator_core && pip install -r requirements.txt

# Testing
test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	pytest tests/ -v --cov=apps --cov-report=html

coverage: ## Generate coverage report
	pytest tests/ --cov=apps --cov-report=html
	@echo "$(GREEN)Report: htmlcov/index.html$(NC)"

# Code Quality
lint: ## Lint code
	@echo "$(GREEN)Linting...$(NC)"
	ruff check apps/
	mypy apps/ --ignore-missing-imports

format: ## Format code
	@echo "$(GREEN)Formatting...$(NC)"
	black apps/
	ruff check --fix apps/

# Cleanup
clean: ## Clean temp files
	@echo "$(YELLOW)Cleaning...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/

clean-all: clean down ## Clean everything
	docker-compose down -v
	docker system prune -f

# Health
health: ## Check service health
	@curl -f http://localhost:8000/health && echo "$(GREEN)✓ Orchestrator$(NC)" || echo "$(RED)✗ Orchestrator$(NC)"
	@curl -f http://localhost:3000 && echo "$(GREEN)✓ Frontend$(NC)" || echo "$(RED)✗ Frontend$(NC)"