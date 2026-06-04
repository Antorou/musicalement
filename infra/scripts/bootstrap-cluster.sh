#!/usr/bin/env bash
# Bootstrap a freshly-applied EKS cluster with the controllers and secret
# wiring that live outside the app Helm chart. Run once after `terraform apply`
# and before the first CI deploy (git push).
#
# Idempotent: safe to re-run. Uses helm upgrade --install throughout.
set -euo pipefail

REGION=eu-west-3
CLUSTER=musicalement
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TF_DIR="$SCRIPT_DIR/../terraform"
K8S_DIR="$SCRIPT_DIR/../k8s"

echo "==> Reading IRSA role ARNs from Terraform outputs"
ESO_ROLE=$(terraform -chdir="$TF_DIR" output -raw irsa_eso_role_arn)
ALB_ROLE=$(terraform -chdir="$TF_DIR" output -raw irsa_alb_role_arn)
EXTDNS_ROLE=$(terraform -chdir="$TF_DIR" output -raw irsa_external_dns_role_arn)

echo "==> Updating kubeconfig"
aws eks update-kubeconfig --name "$CLUSTER" --region "$REGION"

echo "==> Adding Helm repos"
helm repo add external-secrets https://charts.external-secrets.io
helm repo add eks https://aws.github.io/eks-charts
helm repo add external-dns https://kubernetes-sigs.github.io/external-dns/
helm repo update

echo "==> Installing External Secrets Operator"
helm upgrade --install external-secrets external-secrets/external-secrets \
  -n external-secrets --create-namespace \
  --set "serviceAccount.annotations.eks\.amazonaws\.com/role-arn=$ESO_ROLE" \
  --wait

echo "==> Installing AWS Load Balancer Controller"
helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName="$CLUSTER" \
  --set "serviceAccount.annotations.eks\.amazonaws\.com/role-arn=$ALB_ROLE" \
  --wait

echo "==> Installing external-dns"
helm upgrade --install external-dns external-dns/external-dns \
  -n external-dns --create-namespace \
  --set "provider.name=aws" \
  --set "env[0].name=AWS_DEFAULT_REGION" \
  --set "env[0].value=$REGION" \
  --set "serviceAccount.annotations.eks\.amazonaws\.com/role-arn=$EXTDNS_ROLE" \
  --set "policy=sync" \
  --set "txtOwnerId=$CLUSTER" \
  --wait

echo "==> Wiring the app secret via ESO"
kubectl create namespace "$CLUSTER" --dry-run=client -o yaml | kubectl apply -f -
kubectl wait --for condition=established --timeout=120s \
  crd/clustersecretstores.external-secrets.io \
  crd/externalsecrets.external-secrets.io
kubectl apply -f "$K8S_DIR/secret-store.yaml"
kubectl apply -f "$K8S_DIR/external-secret.yaml"

echo
echo "Cluster bootstrap complete. Push to main (or re-run the CI deploy job) to deploy the app."
