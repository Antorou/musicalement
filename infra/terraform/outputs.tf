output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

output "ecr_backend_url" {
  description = "ECR URL for backend image"
  value       = module.ecr.backend_url
}

output "ecr_frontend_url" {
  description = "ECR URL for frontend image"
  value       = module.ecr.frontend_url
}

output "s3_media_bucket" {
  description = "S3 media bucket name"
  value       = module.s3.bucket_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds.endpoint
}

output "rds_password_secret_arn" {
  description = "Secrets Manager ARN holding the RDS master password"
  value       = module.rds.password_secret_arn
}

output "redis_endpoint" {
  description = "ElastiCache Redis primary endpoint"
  value       = module.elasticache.redis_endpoint
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS cluster API endpoint"
  value       = module.eks.cluster_endpoint
}

output "eks_oidc_provider_url" {
  description = "EKS OIDC provider URL (required for IRSA)"
  value       = module.eks.oidc_provider_url
}

output "eks_node_security_group_id" {
  description = "EKS node security group ID"
  value       = module.eks.node_security_group_id
}

output "irsa_app_role_arn" {
  description = "IAM role ARN for the app (S3 media access)"
  value       = module.irsa.app_role_arn
}

output "irsa_eso_role_arn" {
  description = "IAM role ARN for External Secrets Operator"
  value       = module.irsa.eso_role_arn
}

output "irsa_ebs_csi_role_arn" {
  description = "IAM role ARN for the EBS CSI driver"
  value       = module.irsa.ebs_csi_role_arn
}

output "irsa_alb_role_arn" {
  description = "IAM role ARN for the AWS Load Balancer Controller"
  value       = module.irsa.alb_role_arn
}
