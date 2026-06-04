variable "project" {
  type = string
}

variable "account_id" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "cluster_arn" {
  type = string
}

variable "github_repo" {
  description = "GitHub repo in org/repo format"
  type        = string
}
