terraform {
  backend "s3" {
    bucket         = "musicalement-tfstate-c2dbc6c5"
    key            = "musicalement/terraform.tfstate"
    region         = "eu-west-3"
    dynamodb_table = "musicalement-tfstate-lock"
  }
}
