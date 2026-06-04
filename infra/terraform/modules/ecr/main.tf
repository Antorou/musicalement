resource "aws_ecr_repository" "backend" {
  name         = "${var.project}-backend"
  force_delete = true

  encryption_configuration {
    encryption_type = "AES256"
  }
}

resource "aws_ecr_repository" "frontend" {
  name         = "${var.project}-frontend"
  force_delete = true

  encryption_configuration {
    encryption_type = "AES256"
  }
}
