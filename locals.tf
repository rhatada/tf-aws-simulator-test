locals {
  common_tags = {
    Project     = var.project
    ManagedBy   = "terraform"
    Environment = "dev"
  }
}
