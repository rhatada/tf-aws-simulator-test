variable "aws_region" {
  description = "AWSリージョン"
  type        = string
  default     = "ap-northeast-1"
}

variable "project" {
  description = "プロジェクト識別子 (リソース名のプレフィックスに使用)"
  type        = string
  default     = "myapp"
}

variable "db_instance_class" {
  description = "RDSインスタンスクラス"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "初期ストレージ容量 (GiB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Auto Scaling の上限ストレージ容量 (GiB)"
  type        = number
  default     = 100
}

variable "db_name" {
  description = "データベース名"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "マスターユーザー名"
  type        = string
  default     = "dbadmin"
}

variable "db_password" {
  description = "マスターパスワード (terraform.tfvars で設定)"
  type        = string
  sensitive   = true
}
