variable "project" {
  description = "Project name"
  type        = string
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
}

variable "oidc_provider_arn" {
  description = "OIDC provider ARN from the EKS cluster"
  type        = string
}

variable "oidc_provider_url" {
  description = "OIDC provider URL from the EKS cluster (with https://)"
  type        = string
}

variable "s3_media_bucket_arn" {
  description = "ARN of the media S3 bucket"
  type        = string
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID for external-dns"
  type        = string
}
