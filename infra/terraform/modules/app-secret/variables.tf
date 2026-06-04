variable "project" {
  type = string
}

variable "rds_endpoint" {
  type = string
}

variable "rds_password" {
  type      = string
  sensitive = true
}

variable "redis_endpoint" {
  type = string
}

variable "frontend_url" {
  type = string
}

variable "spotify_client_id" {
  type      = string
  sensitive = true
}

variable "spotify_client_secret" {
  type      = string
  sensitive = true
}

variable "spotify_redirect_uri" {
  type = string
}
