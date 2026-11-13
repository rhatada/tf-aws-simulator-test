# AWS Emulator 向けプロバイダー設定
# このファイルは emulator.sh 経由で使う場合にのみ有効にする
# (通常は terraform.tf のプロバイダーが使われる)

provider "aws" {
  region = var.aws_region

  access_key = "EMULATOR424B0B981C76"
  secret_key = "FD1637139D2776FEB12CA328E4D73714E379368F"

  # エミュレーターの全サービスに同じエンドポイントを向ける
  endpoints {
    ec2 = "https://127.0.0.1:9297"
    rds = "https://127.0.0.1:9297"
    sts = "https://127.0.0.1:9297"
  }

  # エミュレーターの自己署名証明書を許可するため
  # CA_BUNDLE を環境変数で渡す (emulator.sh 参照)
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
}
