.PHONY: help build build-china up up-china down restart clean clean-all logs logs-f shell test lint format

# Default compose file (can be overridden by environment variable)
COMPOSE_FILE ?= docker-compose.yml

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "🏗️  Build Commands:"
	@echo "  build       - Build the application image"
	@echo "  build-china - Build with Chinese mirrors (for users in China)"
	@echo ""
	@echo "🚀 Service Commands:"
	@echo "  up          - Build and start all services"
	@echo "  up-china    - Build with Chinese mirrors and start all services"
	@echo "  down        - Stop all services"
	@echo "  restart     - Restart all services"
	@echo ""
	@echo "🧹 Cleanup Commands:"
	@echo "  clean       - Clean up project resources only (safe)"
	@echo "  clean-all   - Clean up ALL Docker resources (dangerous!)"
	@echo ""
	@echo "📊 Monitoring Commands:"
	@echo "  logs        - Show logs for all services"
	@echo "  logs-f      - Follow logs for all services"
	@echo "  health      - Check service health"
	@echo ""
	@echo "🐚 Development Commands:"
	@echo "  shell       - Open shell in server container"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo ""
	@echo "🏠 Local Development:"
	@echo "  local-setup - Set up local development environment"
	@echo "  local-run   - Start local development server"
	@echo "  local-test  - Run tests locally"
	@echo "  local-lint  - Run linting locally"
	@echo "  local-format- Format code locally"
	@echo ""
	@echo "🗄️  Database Commands:"
	@echo "  db-shell    - Open database shell"
	@echo "  db-migrate  - Run database migrations"
	@echo "  db-init     - Initialize database with seed data"
	@echo "  db-setup    - Run migrations and initialize data"
	@echo "  db-reset    - Reset database (downgrade and upgrade)"
	@echo ""
	@echo "📦 Poetry Commands:"
	@echo "  poetry-install - Install dependencies with Poetry"
	@echo "  poetry-update  - Update dependencies with Poetry"
	@echo "  poetry-shell   - Start Poetry shell"
	@echo ""
	@echo "🇨🇳 For users in China, use *-china commands for faster builds"

# Build application image (default - no mirrors)
build:
	@echo "🔨 Building application image..."
	docker compose -f $(COMPOSE_FILE) build server
	@echo "✅ Build completed!"

# Build with Chinese mirrors
build-china:
	@echo "🔨 Building application image with Chinese mirrors..."
	docker compose -f $(COMPOSE_FILE) build --build-arg USE_CHINA_MIRROR=true server
	@echo "✅ Build completed!"

# Start all services (build first, then start)
up: build
	@echo "🚀 Starting all services..."
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "✅ All services started!"
	@echo "📝 Server: http://localhost:5001"
	@echo "📝 API Docs: http://localhost:5001/docs"
	@echo "📝 Health: http://localhost:5001/health"

# Start all services with Chinese mirrors
up-china: build-china
	@echo "🚀 Starting all services..."
	docker compose -f $(COMPOSE_FILE) up -d
	@echo "✅ All services started!"
	@echo "📝 Server: http://localhost:5001"
	@echo "📝 API Docs: http://localhost:5001/docs"
	@echo "📝 Health: http://localhost:5001/health"

# Stop all services
down:
	@echo "🛑 Stopping all services..."
	docker compose -f $(COMPOSE_FILE) down
	@echo "✅ All services stopped!"

# Restart all services
restart: down up

# Clean up project resources only
clean:
	@echo "🧹 Cleaning up project resources..."
	docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker compose -f $(COMPOSE_FILE) rm -f
	@if [ -n "$$(docker images -q funiq-ai-backend*)" ]; then \
		echo "Removing project images..."; \
		docker rmi $$(docker images -q funiq-ai-backend*) || true; \
	fi
	@echo "✅ Project cleanup completed!"

# Clean up everything (dangerous - use with caution)
clean-all:
	@echo "⚠️  WARNING: This will clean ALL Docker resources on your system!"
	@echo "Are you sure? This action cannot be undone."
	@read -p "Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ] || exit 1
	@echo "🧹 Cleaning up all Docker resources..."
	docker compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker system prune -af
	docker volume prune -f
	@echo "✅ System-wide cleanup completed!"

# Show logs
logs:
	docker compose -f $(COMPOSE_FILE) logs

# Follow logs
logs-f:
	docker compose -f $(COMPOSE_FILE) logs -f

# Open shell in server container
shell:
	docker compose -f $(COMPOSE_FILE) exec server bash

# Run tests
test:
	docker compose -f $(COMPOSE_FILE) exec server python -m pytest

# Run linting
lint:
	docker compose -f $(COMPOSE_FILE) exec server python -m ruff check .

# Format code
format:
	docker compose -f $(COMPOSE_FILE) exec server python -m ruff format .
	docker compose -f $(COMPOSE_FILE) exec server python -m ruff check . --fix

# Development shortcuts
dev-build:
	@echo "🔨 Building for development..."
	docker compose -f $(COMPOSE_FILE) build --no-cache server

dev-up: dev-build
	@echo "🚀 Starting development environment..."
	docker compose -f $(COMPOSE_FILE) up

# Production shortcuts
prod-build:
	@echo "🔨 Building for production..."
	docker compose -f $(COMPOSE_FILE) build --no-cache server

prod-up: prod-build
	@echo "🚀 Starting production environment..."
	docker compose -f $(COMPOSE_FILE) up -d

# Health check
health:
	@echo "🏥 Checking service health..."
	@curl -f http://localhost:5001/health || echo "❌ Server not healthy"
	@docker compose -f $(COMPOSE_FILE) ps

# Database operations
db-shell:
	docker compose -f $(COMPOSE_FILE) exec db psql -U postgres -d $${POSTGRES_DB:-funiq_ai_db}

db-migrate:
	docker compose -f $(COMPOSE_FILE) exec server python -m alembic upgrade head

db-init:
	docker compose -f $(COMPOSE_FILE) exec server sh -c "cd /app && PYTHONPATH=/app python scripts/init_data.py"

db-setup: db-migrate db-init

db-reset:
	docker compose -f $(COMPOSE_FILE) exec server python -m alembic downgrade base
	docker compose -f $(COMPOSE_FILE) exec server python -m alembic upgrade head

# Poetry operations (for local development)
poetry-install:
	@echo "📦 Installing dependencies with Poetry..."
	poetry install

poetry-update:
	@echo "🔄 Updating dependencies with Poetry..."
	poetry update

poetry-shell:
	@echo "🐚 Starting Poetry shell..."
	poetry shell

# Local development (without Docker)
local-setup: poetry-install
	@echo "🏠 Setting up local development environment..."
	@echo "Make sure PostgreSQL and Redis are running locally"
	@echo "Copy .env.example to .env and configure your settings"

local-run:
	@echo "🚀 Starting local development server..."
	poetry run python app.py

local-test:
	@echo "🧪 Running tests locally..."
	poetry run pytest

local-lint:
	@echo "🔍 Running linting locally..."
	poetry run ruff check .

local-format:
	@echo "🎨 Formatting code locally..."
	poetry run ruff format .
	poetry run ruff check . --fix
