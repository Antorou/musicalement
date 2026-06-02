output "state_bucket_name" {
  value       = aws_s3_bucket.tfstate.bucket
  description = "Copy into backend.hcl as 'bucket'"
}

output "dynamodb_table_name" {
  value       = aws_dynamodb_table.tfstate_lock.name
  description = "Copy into backend.hcl as 'dynamodb_table'"
}

output "aws_region" {
  value       = var.aws_region
  description = "Copy into backend.hcl as 'region'"
}
