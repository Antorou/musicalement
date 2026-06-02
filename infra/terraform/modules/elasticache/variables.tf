variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "eks_node_sg_id" {
  type        = string
  description = "EKS node security group ID allowed to reach Redis"
}

variable "tags" {
  type    = map(string)
  default = {}
}
