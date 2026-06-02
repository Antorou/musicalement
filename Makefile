.PHONY: up down migrate shell test logs

up:
	docker compose up --build

down:
	docker compose down

migrate:
	docker compose run --rm web python manage.py migrate

shell:
	docker compose run --rm web python manage.py shell

test:
	docker compose run --rm web pytest

logs:
	docker compose logs -f
