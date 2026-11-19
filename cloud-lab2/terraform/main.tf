provider "aws" {
  region              = var.aws_region
  profile             = "lab2"
  allowed_account_ids = ["707256068187"]

  default_tags {
    tags = {
      Project   = var.project_name
      ManagedBy = "Terraform"
      Lab       = "Cloud-Lab-2"
    }
  }
}