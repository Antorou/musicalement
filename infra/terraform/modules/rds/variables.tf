variable "project" {
  description = "Project name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs for the DB subnet group"
  type        = list(string)
}

variable "eks_node_sg_id" {
  description = "EKS node security group ID — wires the RDS ingress rule; leave empty until ANT-32"
  type        = string
  default     = ""
}
