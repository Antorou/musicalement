resource "random_password" "django_secret_key" {
  length  = 64
  special = false
}

locals {
  rds_host = split(":", var.rds_endpoint)[0]
  rds_port = split(":", var.rds_endpoint)[1]
}

resource "aws_secretsmanager_secret" "app" {
  name                    = "${var.project}/app"
  recovery_window_in_days = 0

  tags = { Project = var.project }
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    SECRET_KEY                = random_password.django_secret_key.result
    ALLOWED_HOSTS             = "www.${trimprefix(trimprefix(var.frontend_url, "https://"), "http://")}"
    DJANGO_SETTINGS_MODULE    = "${var.project}.settings.prod"
    POSTGRES_DB               = var.project
    POSTGRES_USER             = var.project
    POSTGRES_PASSWORD         = var.rds_password
    POSTGRES_HOST             = local.rds_host
    POSTGRES_PORT             = local.rds_port
    REDIS_URL                 = "redis://${var.redis_endpoint}:6379/0"
    FRONTEND_URL              = var.frontend_url
    SPOTIFY_CLIENT_ID         = var.spotify_client_id
    SPOTIFY_CLIENT_SECRET     = var.spotify_client_secret
    SPOTIFY_REDIRECT_URI      = var.spotify_redirect_uri
  })
}
