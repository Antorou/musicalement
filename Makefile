.PHONY: up down migrate shell test logs lint build-backend build-frontend \
        tf-bootstrap-init tf-bootstrap-apply \
        tf-init tf-plan tf-apply tf-destroy tf-output

TF_BOOTSTRAP_DIR := infra/bootstrap
TF_DIR           := infra/terraform
TF_BACKEND_CFG   := infra/terraform/backend.hcl

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
