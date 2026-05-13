# ScopeIQ Makefile
# Streamlined commands for frontend, backend, and DevOps workflows
#
# Usage: make <target>
# Example: make dev, make test, make deploy

.PHONY: help dev stop clean test lint typecheck \
        migrate migration-down logs db-shell redis-shell \
        build build-prod deploy deploy-init setup env-check

# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────

DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_PROD = docker compose -f docker-compose.prod.yml
PYTHON = uv run
BACKEND_DIR = backend
FRONTEND_DIR = frontend

# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────

help: ## Show this help message
	@echo "ScopeIQ - AI-powered idea validation tool"
	@echo ""
	@echo "Usage: make <target>"
	@echo ""
	@echo "Development:"
	@echo "  dev              Start all services (local development)"
	@echo "  stop             Stop all services"
	@echo "  clean            Stop and remove volumes (fresh start)"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  test             Run backend tests"
	@echo "  lint             Run linters (backend + frontend)"
	@echo "  typecheck        Run type checkers (backend + frontend)"
	@echo "  format           Format code"
	@echo ""
	@echo "Database:"
	@echo "  migrate          Run database migrations"
	@echo "  migration-down   Rollback last migration"
	@echo "  db-shell         Open psql shell to database"
	@echo "  redis-shell      Open redis-cli shell"
	@echo "  logs             View all logs"
	@echo ""
	@echo "Build:"
	@echo "  build            Build all Docker images"
	@echo "  build-prod       Build production Docker images"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy           Deploy to production VPS"
	@echo "  deploy-init      Initialize VPS (one-time setup)"
	@echo ""
	@echo "Setup:"
	@echo "  setup            Initial project setup"
	@echo "  env-check        Validate .env file"

# ─────────────────────────────────────────────────────────────────────────────
# Development
# ─────────────────────────────────────────────────────────────────────────────

dev: env-check ## Start all services (local development)
	@echo "▶️  Starting all services..."
	$(DOCKER_COMPOSE) up --build

stop: ## Stop all services
	@echo "⏹️  Stopping all services..."
	$(DOCKER_COMPOSE) down

clean: ## Stop and remove volumes (WARNING: deletes all data!)
	@echo "⚠️  Stopping and removing all volumes..."
	$(DOCKER_COMPOSE) down -v
	@echo "✅ Clean complete. Run 'make dev' to start fresh."

# ─────────────────────────────────────────────────────────────────────────────
# Testing & Quality
# ─────────────────────────────────────────────────────────────────────────────

test: ## Run backend tests
	@echo "▶️  Running backend tests..."
	cd $(BACKEND_DIR) && $(PYTHON) pytest -v

lint: lint-backend lint-frontend ## Run linters (backend + frontend)

lint-backend: ## Run backend linter (ruff)
	@echo "▶️  Running ruff on backend..."
	cd $(BACKEND_DIR) && $(PYTHON) ruff check .

lint-frontend: ## Run frontend linter (eslint)
	@echo "▶️  Running eslint on frontend..."
	@if command -v pnpm >/dev/null 2>&1; then \
		cd $(FRONTEND_DIR) && pnpm lint; \
	else \
		echo "⚠️  pnpm not found. Install with: npm install -g pnpm"; \
		exit 1; \
	fi

format: format-backend format-frontend ## Format code

format-backend: ## Format backend code
	@echo "▶️  Formatting backend code..."
	cd $(BACKEND_DIR) && $(PYTHON) ruff format .

format-frontend: ## Format frontend code
	@echo "▶️  Formatting frontend code..."
	@if command -v pnpm >/dev/null 2>&1; then \
		cd $(FRONTEND_DIR) && pnpm prettier --write "src/**/*.{ts,tsx}"; \
	else \
		echo "⚠️  pnpm not found. Install with: npm install -g pnpm"; \
		exit 1; \
	fi

typecheck: typecheck-backend typecheck-frontend ## Run type checkers

typecheck-backend: ## Run backend type checker (mypy)
	@echo "▶️  Running mypy on backend..."
	cd $(BACKEND_DIR) && $(PYTHON) mypy app

typecheck-frontend: ## Run frontend type checker (tsc)
	@echo "▶️  Running typecheck on frontend..."
	@if command -v pnpm >/dev/null 2>&1; then \
		cd $(FRONTEND_DIR) && pnpm typecheck; \
	else \
		echo "⚠️  pnpm not found. Install with: npm install -g pnpm"; \
		exit 1; \
	fi

# ─────────────────────────────────────────────────────────────────────────────
# Database
# ─────────────────────────────────────────────────────────────────────────────

migrate: ## Run database migrations
	@echo "▶️  Running database migrations..."
	$(DOCKER_COMPOSE) exec api alembic upgrade head

migration-down: ## Rollback last migration
	@echo "⏪ Rolling back last migration..."
	$(DOCKER_COMPOSE) exec api alembic downgrade -1

db-shell: ## Open psql shell to database
	@echo "🐘 Opening psql shell..."
	$(DOCKER_COMPOSE) exec db psql -U scopeiq

redis-shell: ## Open redis-cli shell
	@echo "🔴 Opening redis-cli shell..."
	$(DOCKER_COMPOSE) exec redis redis-cli

logs: ## View all logs
	$(DOCKER_COMPOSE) logs -f

# ─────────────────────────────────────────────────────────────────────────────
# Build
# ─────────────────────────────────────────────────────────────────────────────

build: ## Build all Docker images
	@echo "🔨 Building all Docker images..."
	$(DOCKER_COMPOSE) build

build-prod: ## Build production Docker images
	@echo "🔨 Building production Docker images..."
	$(DOCKER_COMPOSE_PROD) build

# ─────────────────────────────────────────────────────────────────────────────
# Deployment
# ─────────────────────────────────────────────────────────────────────────────

deploy: ## Deploy to production VPS
	@echo "🚀 Deploying to production VPS..."
	@echo "📋 Ensure you've already:"
	@echo "   1. Run 'make deploy-init' (one-time VPS setup)"
	@echo "   2. Copied .env to the VPS"
	@echo ""
	@read -p "Press Enter to continue or Ctrl+C to cancel..." && \
	echo "▶️  Deploying..." && \
	ssh scopeiq@$$(cat .env | grep VPS_IP | cut -d'=' -f2) 'cd ~/scopeiq && \
	docker compose -f docker-compose.prod.yml up -d --build && \
	docker compose -f docker-compose.prod.yml exec fastapi alembic upgrade head'
	@echo "✅ Deploy complete!"

deploy-init: ## Initialize VPS (one-time setup)
	@echo "🔧 Initializing VPS (one-time setup)..."
	@echo "📋 This will:"
	@echo "   1. Update system packages"
	@echo "   2. Create scopeiq user"
	@echo "   3. Harden SSH configuration"
	@echo "   4. Install Docker"
	@echo "   5. Configure firewall"
	@echo ""
	@read -p "Enter VPS IP address: " VPS_IP && \
	echo "▶️  Running setup script..." && \
	scp deploy/setup-vps.sh root@$$VPS_IP: && \
	ssh root@$$VPS_IP 'bash setup-vps.sh'
	@echo "✅ VPS initialized! Add your SSH keys to /home/scopeiq/.ssh/authorized_keys"

# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────

setup: env-check ## Initial project setup
	@echo "🔧 Setting up project..."
	@echo "▶️  Installing backend dependencies..."
	cd $(BACKEND_DIR) && uv sync
	@echo "▶️  Installing frontend dependencies..."
	@if command -v pnpm >/dev/null 2>&1; then \
		cd $(FRONTEND_DIR) && pnpm install; \
	else \
		echo "⚠️  pnpm not found. Install with: npm install -g pnpm"; \
		exit 1; \
	fi
	@echo "▶️  Installing pre-commit..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install --system pre-commit; \
	elif command -v pipx >/dev/null 2>&1; then \
		pipx install pre-commit; \
	else \
		pip3 install --user pre-commit; \
	fi
	pre-commit install
	@echo "✅ Setup complete!"

env-check: ## Validate .env file
	@echo "🔍 Checking .env file..."
	@if [ ! -f .env ]; then \
		echo "⚠️  .env not found. Copying from .env.example..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and fill in your API keys!"; \
		exit 1; \
	fi
	@echo "✅ .env exists"
