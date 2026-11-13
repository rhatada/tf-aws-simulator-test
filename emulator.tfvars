# AWS Emulator 用変数
# terraform apply -var-file=emulator.tfvars で使用

aws_region = "ap-northeast-1"
project    = "myapp"

db_instance_class        = "db.t3.micro"
db_allocated_storage     = 20
db_max_allocated_storage = 100

db_name     = "appdb"
db_username = "dbadmin"
db_password = "emulator-test-password"
