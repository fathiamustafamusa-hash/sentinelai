.PHONY: help up down build test lint format security clean prod-up prod-down

help:
	@echo "SentinelAI - Available commands:"
	@echo "  make up           - Start dev environment"
	@echo "  make down         - Stop dev environment"
	@echo "  make build        - Build all images"
	@echo "  make test         - Run tests with coverage"
	@echo "  make lint         - Run ruff check"
	@echo "  make format       - Run ruff format"
	@echo "  make security     - Run bandit + pip-audit"
	@echo "  make clean        - Remove containers and volumes"
	@echo "  make prod-up      - Start production stack"
	@echo "  make prod-down    - Stop production stack"

up:
	docker compose up -d
	@echo "Backend: http://localhost:8000"
	@echo "Docs:    http://localhost:8000/docs"

down:
	docker compose down

build:
	docker compose build --no-cache

test:
	cd src/backend && poetry run pytest tests/ -v --cov=app

lint:
	cd src/backend && poetry run ruff check app

format:
	cd src/backend && poetry run ruff format app

security:
	cd src/backend && poetry run bandit -r app -c pyproject.toml

clean:
	docker compose down -v
	docker system prune -f

prod-up:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down
