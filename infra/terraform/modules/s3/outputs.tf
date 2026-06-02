output "avatars_bucket_name" {
  value = aws_s3_bucket.avatars.bucket
}

output "frontend_bucket_name" {
  value = aws_s3_bucket.frontend.bucket
}

output "avatars_bucket_arn" {
  value = aws_s3_bucket.avatars.arn
}

output "frontend_bucket_arn" {
  value = aws_s3_bucket.frontend.arn
}
