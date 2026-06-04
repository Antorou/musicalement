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
