output "db_endpoint" {
  description = "RDS エンドポイント (ホスト:ポート)"
  value       = aws_db_instance.main.endpoint
}

output "db_host" {
  description = "RDS ホスト名"
  value       = aws_db_instance.main.address
}

output "db_port" {
  description = "RDS ポート番号"
  value       = aws_db_instance.main.port
}

output "db_name" {
  description = "データベース名"
  value       = aws_db_instance.main.db_name
}

output "db_username" {
  description = "マスターユーザー名"
  value       = aws_db_instance.main.username
  sensitive   = true
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}
