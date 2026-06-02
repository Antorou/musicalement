variable "aws_region" {
  type        = string
  default     = "eu-west-3"
  description = "AWS region for the state bucket"
}

variable "project_name" {
  type        = string
  default     = "musicalement"
  description = "Project name prefix for resource names"
}
