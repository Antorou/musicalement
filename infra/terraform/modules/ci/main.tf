# GitHub Actions OIDC provider
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

  tags = { Project = var.project }
}

# CI IAM role — trusted by GitHub Actions on main branch only
data "aws_iam_policy_document" "ci_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repo}:ref:refs/heads/main"]
    }
  }
}

resource "aws_iam_role" "ci" {
  name               = "${var.project}-ci"
  assume_role_policy = data.aws_iam_policy_document.ci_trust.json

  tags = { Project = var.project }
}

# ECR push + EKS describe permissions
data "aws_iam_policy_document" "ci" {
  statement {
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
    ]
    resources = [
      "arn:aws:ecr:${var.aws_region}:${var.account_id}:repository/${var.project}-backend",
      "arn:aws:ecr:${var.aws_region}:${var.account_id}:repository/${var.project}-frontend",
    ]
  }
  statement {
    effect    = "Allow"
    actions   = ["eks:DescribeCluster"]
    resources = [var.cluster_arn]
  }
}

resource "aws_iam_role_policy" "ci" {
  name   = "ci-deploy"
  role   = aws_iam_role.ci.id
  policy = data.aws_iam_policy_document.ci.json
}

# EKS access entry — cluster-admin for the CI role
resource "aws_eks_access_entry" "ci" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.ci.arn
  type          = "STANDARD"

  tags = { Project = var.project }
}

resource "aws_eks_access_policy_association" "ci" {
  cluster_name  = var.cluster_name
  principal_arn = aws_iam_role.ci.arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }
}
