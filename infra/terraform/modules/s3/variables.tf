variable "project" {
  description = "Project name used as bucket name prefix"
  type        = string
}

variable "account_id" {
  description = "AWS account ID used as bucket name suffix for global uniqueness"
  type        = string
}
