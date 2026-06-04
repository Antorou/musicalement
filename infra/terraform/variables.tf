variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "eu-west-3"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "musicalement"
}

variable "domain" {
  description = "Root domain name"
  type        = string
  default     = "antorou.online"
}

variable "route53_zone_id" {
  description = "Route53 hosted zone ID (bootstrap - never destroyed)"
  type        = string
  default     = "Z05338593KPD844KJ8P5K"
}

variable "spotify_client_id" {
  description = "Spotify OAuth client ID"
  type        = string
  sensitive   = true
}

variable "spotify_client_secret" {
  description = "Spotify OAuth client secret"
  type        = string
  sensitive   = true
}

