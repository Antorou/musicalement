variable "project" {
  type = string
}

variable "zone_id" {
  description = "Route53 hosted zone ID (bootstrap resource - never destroyed)"
  type        = string
}

variable "domain" {
  description = "Root domain name"
  type        = string
}

variable "aws_region" {
  type = string
}
