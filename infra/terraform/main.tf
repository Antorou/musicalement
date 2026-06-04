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
