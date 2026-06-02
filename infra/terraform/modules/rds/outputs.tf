output "endpoint" {
  value     = aws_db_instance.postgres.endpoint
  sensitive = true
}

output "address" {
  value     = aws_db_instance.postgres.address
  sensitive = true
}

output "port" {
  value = aws_db_instance.postgres.port
}

output "db_name" {
  value = aws_db_instance.postgres.db_name
}
