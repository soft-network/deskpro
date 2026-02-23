BACKEND_DIR  := deskpro-backend
FRONTEND_DIR := Frontend/frontendnext

.PHONY: help setup dev backend frontend migrate makemigrations \
        create-admin test docker-up docker-down clean

help:
	@echo ""
	@echo "  make setup          First-time setup: deps, migrate, create-admin"
	@echo "  make dev            Start backend + frontend in parallel"
	@echo "  make backend        Start Django backend only  (port 8000)"
	@echo "  make frontend       Start Next.js frontend only (port 3000)"
	@echo "  make migrate        Run Django migrations"
	@echo "  make makemigrations Create new Django migration files"
	@echo "  make create-admin   Create / update SaaS admin account"
	@echo "  make test           Run backend test suite"
	@echo "  make docker-up      Build + start all services via Docker Compose"
	@echo "  make docker-down    Stop + remove Docker containers"
	@echo "  make clean          Remove .venv, node_modules, .next"
	@echo ""

# ---------------------------------------------------------------------------
# First-time setup
# ---------------------------------------------------------------------------

setup: _check-env-backend _check-env-frontend
	@echo "==> Installing backend dependencies..."
	cd $(BACKEND_DIR) && uv sync
	@echo "==> Running migrations..."
	cd $(BACKEND_DIR) && DJANGO_ENV=dev uv run manage.py migrate
	@echo "==> Creating SaaS admin..."
	cd $(BACKEND_DIR) && DJANGO_ENV=dev uv run manage.py create_saas_admin
	@echo ""
	@echo "==> Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && npm install
	@echo ""
	@echo "Setup complete — run 'make dev' to start."

_check-env-backend:
	@test -f $(BACKEND_DIR)/.env.dev || { \
		cp $(BACKEND_DIR)/.env.example $(BACKEND_DIR)/.env.dev; \
		echo ""; \
		echo "  Created $(BACKEND_DIR)/.env.dev from .env.example."; \
		echo "  Fill in your credentials, then re-run 'make setup'."; \
		echo ""; \
		exit 1; \
	}

_check-env-frontend:
	@test -f $(FRONTEND_DIR)/.env.local || \
		cp $(FRONTEND_DIR)/.env.example $(FRONTEND_DIR)/.env.local

# ---------------------------------------------------------------------------
# Dev servers
# ---------------------------------------------------------------------------

dev:
	$(MAKE) -j2 backend frontend

backend:
	cd $(BACKEND_DIR) && DJANGO_ENV=dev uv run manage.py runserver

frontend:
	cd $(FRONTEND_DIR) && npm run dev

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

migrate:
	cd $(BACKEND_DIR) && DJANGO_ENV=dev uv run manage.py migrate

makemigrations:
	cd $(BACKEND_DIR) && DJANGO_ENV=dev uv run manage.py makemigrations

create-admin:
	cd $(BACKEND_DIR) && DJANGO_ENV=dev uv run manage.py create_saas_admin

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

test:
	cd $(BACKEND_DIR) && DJANGO_ENV=dev uv run pytest

# ---------------------------------------------------------------------------
# Docker
# ---------------------------------------------------------------------------

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean:
	rm -rf $(BACKEND_DIR)/.venv
	rm -rf $(FRONTEND_DIR)/node_modules $(FRONTEND_DIR)/.next
