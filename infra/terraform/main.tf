module "vpc" {
  source  = "./modules/vpc"
  project = var.project
}

module "ecr" {
  source  = "./modules/ecr"
  project = var.project
}

module "s3" {
  source     = "./modules/s3"
  project    = var.project
  account_id = data.aws_caller_identity.current.account_id
}

module "rds" {
  source             = "./modules/rds"
  project            = var.project
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  eks_node_sg_id     = var.eks_node_sg_id
}
