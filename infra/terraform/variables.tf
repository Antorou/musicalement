variable "aws_region" {
  type    = string
  default = "eu-west-3"
}

variable "project_name" {
  type    = string
  default = "musicalement"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "db_name" {
  type    = string
  default = "musicalement"
}

variable "db_username" {
  type    = string
  default = "musicalement"
}

variable "db_password" {
  type      = string
  sensitive = true
}
