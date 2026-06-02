output "vpc_id" {
  value = module.vpc.vpc_id
}

output "ecr_backend_url" {
  value = module.ecr.backend_repository_url
}

output "ecr_frontend_url" {
  value = module.ecr.frontend_repository_url
}

output "rds_endpoint" {
  value     = module.rds.endpoint
  sensitive = true
}

output "elasticache_endpoint" {
  value = module.elasticache.endpoint
}

output "elasticache_port" {
  value = module.elasticache.port
}

output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  value     = module.eks.cluster_endpoint
  sensitive = true
}

output "eks_oidc_provider_arn" {
  value = module.eks.oidc_provider_arn
}

output "s3_avatars_bucket" {
  value = module.s3.avatars_bucket_name
}

output "s3_frontend_bucket" {
  value = module.s3.frontend_bucket_name
}
