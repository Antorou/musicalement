.PHONY: up down migrate shell logs test lint

up:
	docker compose up

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

shell:
	docker compose exec web python manage.py shell

logs:
	docker compose logs -f

test:
	docker compose run --rm web sh -c "pip install -q -r requirements-dev.txt && pytest"

lint:
	docker compose run --rm web sh -c "pip install -q -r requirements-dev.txt && ruff check ."
	cd frontend && npm run lint
