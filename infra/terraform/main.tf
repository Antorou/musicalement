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

module "eks" {
  source             = "./modules/eks"
  project            = var.project
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
}

module "rds" {
  source             = "./modules/rds"
  project            = var.project
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  eks_node_sg_id     = module.eks.node_security_group_id
}

module "elasticache" {
  source             = "./modules/elasticache"
  project            = var.project
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  eks_node_sg_id     = module.eks.node_security_group_id
}

module "ci" {
  source       = "./modules/ci"
  project      = var.project
  account_id   = data.aws_caller_identity.current.account_id
  aws_region   = var.aws_region
  cluster_name = module.eks.cluster_name
  cluster_arn  = module.eks.cluster_arn
  github_repo  = "Antorou/musicalement"
}

module "irsa" {
  source              = "./modules/irsa"
  project             = var.project
  cluster_name        = module.eks.cluster_name
  oidc_provider_arn   = module.eks.oidc_provider_arn
  oidc_provider_url   = module.eks.oidc_provider_url
  s3_media_bucket_arn = module.s3.bucket_arn
}
