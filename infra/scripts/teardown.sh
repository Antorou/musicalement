#!/usr/bin/env bash
# Clean teardown. The ALB and the Route53 www record are created by in-cluster
# controllers, not by Terraform. They MUST be removed (by deleting the Ingress)
# before `terraform destroy`, or the orphaned ALB ENIs/SGs block the VPC destroy
# and the Route53 records are left dangling.
#
# Order: delete app release -> let external-dns/LBC process deletions ->
# uninstall controllers -> terraform destroy.
set -euo pipefail

REGION=eu-west-3
CLUSTER=musicalement
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TF_DIR="$SCRIPT_DIR/../terraform"

aws eks update-kubeconfig --name "$CLUSTER" --region "$REGION" || true

echo "==> Deleting app release (removes Ingress -> ALB + Route53 records)"
helm uninstall "$CLUSTER" -n "$CLUSTER" || true
kubectl delete ingress --all -n "$CLUSTER" --ignore-not-found

echo "==> Waiting for external-dns and the LBC to process deletions (90s)"
sleep 90

echo "==> Uninstalling controllers"
helm uninstall external-dns -n external-dns || true
helm uninstall aws-load-balancer-controller -n kube-system || true
helm uninstall external-secrets -n external-secrets || true

echo "==> terraform destroy"
terraform -chdir="$TF_DIR" destroy -auto-approve

echo
echo "Teardown complete. Bootstrap stack (S3 state, DynamoDB lock, Route53 zone) preserved."
