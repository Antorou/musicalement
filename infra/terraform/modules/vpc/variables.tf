variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "azs" {
  type        = list(string)
  description = "List of AZs to use (pass 3)"
}

variable "tags" {
  type    = map(string)
  default = {}
}
