.PHONY: up down migrate shell test logs lint \
        build-backend build-frontend build prod-check \
        tf-bootstrap-init tf-bootstrap-apply \
        tf-init tf-plan tf-apply tf-destroy tf-output

TF_BOOTSTRAP_DIR := infra/bootstrap
TF_DIR           := infra/terraform
TF_BACKEND_CFG   := infra/terraform/backend.hcl

# --- local dev (settings: musicalement.settings.local) ---
# docker-compose overrides the image's baked-in prod setting back to local.

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
# The web image is built from requirements.txt (prod) and has no test/lint tools,
# so install requirements-dev.txt into the throwaway container first.

test:
	docker compose run --rm web sh -c "pip install -q -r requirements-dev.txt && pytest"

lint:
	docker compose run --rm web sh -c "pip install -q -r requirements-dev.txt && ruff check ."
	cd frontend && npm run lint

# --- production images (settings: musicalement.settings.prod) ---
# prod.py has no secret defaults: it requires SECRET_KEY, ALLOWED_HOSTS, POSTGRES_*,
# REDIS_URL, SPOTIFY_*, and FRONTEND_URL to be set, and crashes on startup if any is missing.

build-backend:
	docker build -t musicalement-backend:local backend/

build-frontend:
	docker build -t musicalement-frontend:local frontend/

build: build-backend build-frontend

# Smoke-test that the prod backend image boots under prod.py (catches the
# missing-env crashes prod.py raises on startup). Reuses dev secrets from .env
# and supplies the vars prod.py requires but .env omits (local.py defaults them).
# `check --deploy` only loads settings, so placeholder DB host/port are fine.
prod-check: build-backend
	docker run --rm --env-file .env \
		-e DJANGO_SETTINGS_MODULE=musicalement.settings.prod \
		-e ALLOWED_HOSTS=localhost \
		-e POSTGRES_HOST=db \
		-e POSTGRES_PORT=5432 \
		musicalement-backend:local \
		python manage.py check --deploy

# --- terraform bootstrap (run once, never destroy) ---

tf-bootstrap-init:
	terraform -chdir=$(TF_BOOTSTRAP_DIR) init

tf-bootstrap-apply:
	terraform -chdir=$(TF_BOOTSTRAP_DIR) apply
	@echo ""
	@echo "Copy the outputs above into $(TF_BACKEND_CFG)"

# --- terraform main infra (apply/destroy daily) ---

tf-init:
	@test -f $(TF_BACKEND_CFG) || (echo "ERROR: $(TF_BACKEND_CFG) not found. Copy backend.hcl.example and fill in the bucket name." && exit 1)
	terraform -chdir=$(TF_DIR) init -backend-config=../../$(TF_BACKEND_CFG) -reconfigure

tf-plan:
	terraform -chdir=$(TF_DIR) plan -var-file=terraform.tfvars

tf-apply:
	terraform -chdir=$(TF_DIR) apply -var-file=terraform.tfvars

tf-output:
	terraform -chdir=$(TF_DIR) output

# Before destroying: delete any k8s Ingress/LoadBalancer services first to
# avoid orphaned ALBs that block VPC teardown.
#   kubectl delete ingress --all -A
#   kubectl delete svc --field-selector spec.type=LoadBalancer -A
tf-destroy:
	terraform -chdir=$(TF_DIR) destroy -var-file=terraform.tfvars
