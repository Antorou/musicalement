.PHONY: up down migrate shell test logs lint build-backend build-frontend

# --- local dev ---

up:
	docker compose up --build

down:
	docker compose down

migrate:
	docker compose run --rm web python manage.py migrate

shell:
	docker compose run --rm web python manage.py shell

logs:
	docker compose logs -f

# --- quality ---

test:
	docker compose run --rm web pytest

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

# --- production image builds ---

build-backend:
	docker build -t musicalmente-backend:local backend/

build-frontend:
	docker build -t musicalement-frontend:local frontend/
