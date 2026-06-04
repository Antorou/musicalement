output "app_role_arn" {
  value = aws_iam_role.app.arn
}

output "eso_role_arn" {
  value = aws_iam_role.eso.arn
}

output "ebs_csi_role_arn" {
  value = aws_iam_role.ebs_csi.arn
}

output "alb_role_arn" {
  value = aws_iam_role.alb.arn
}
