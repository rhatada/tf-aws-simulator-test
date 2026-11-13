# tf-aws-simulator-test

AWS Emulator を使って、Terraform で RDS を払い出すコードをローカルで検証するサンプルプロジェクトです。
AWS アカウント・実費不要でインフラのテストが完結します。

---

## 技術スタック

| 分類 | ツール / バージョン |
|---|---|
| IaC | [Terraform](https://developer.hashicorp.com/terraform) >= 1.6 |
| AWS Provider | hashicorp/aws ~> 5.0 |
| エミュレーター | [AWS Emulator](https://github.com/aws/aws-emulator) (Rust 製・AWS 公式) |
| テストフレームワーク | [Behave](https://behave.readthedocs.io/) 1.3+ (Gherkin / BDD) |
| AWS SDK | [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) |
| 言語 | Python 3.x |
| ビルド | Rust / Cargo (エミュレーターをソースからビルドする場合) |

### 対象 AWS リソース

- VPC / Subnet (private × 2 AZ)
- Security Group (RDS 用 inbound 5432/TCP)
- DB Subnet Group
- DB Parameter Group (PostgreSQL 15)
- RDS Instance (PostgreSQL 15 / db.t3.micro / gp3 / 暗号化有効)

---

## 前提条件

| ツール | インストール方法 |
|---|---|
| Terraform >= 1.6 | https://developer.hashicorp.com/terraform/install |
| Python >= 3.9 | OS パッケージマネージャーまたは pyenv |
| AWS Emulator バイナリ | 下記「エミュレーターのセットアップ」参照 |

```bash
pip install behave boto3
```

---

## エミュレーターのセットアップ

### ソースからビルド（Linux x86_64 / aarch64）

```bash
# 依存ツール
rustup  # https://rustup.rs
sudo dnf install -y gcc   # または apt install gcc

# クローン & ビルド（初回は大容量・長時間）
git clone https://github.com/aws/aws-emulator.git
cd aws-emulator
cargo build -p aws-emulator-router

# バイナリ確認
./target/debug/aws-emulator --version
```

> **注意**: `target/` ディレクトリは 70GB 以上になります。テスト後に `cargo clean` で回収できます。

### エミュレーター起動

```bash
./target/debug/aws-emulator \
  --port 9297 \
  --telemetry off \
  --auth off \
  > /tmp/aws-emulator.log 2>&1 &

# 起動確認
curl -sk https://127.0.0.1:9297/__admin/health
# => ok
```

---

## テスト実行手順

### 1. 環境変数を設定

```bash
export AWS_CA_BUNDLE=~/.aws/emulator/9297/ca.pem
export AWS_ENDPOINT_URL=https://127.0.0.1:9297
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=ap-northeast-1
```

### 2. Terraform で RDS を払い出す

```bash
terraform init
terraform apply -var-file=emulator.tfvars -auto-approve
```

### 3. Gherkin テストを実行

```bash
python3 -m behave
```

成功時の出力例:

```
1 feature passed, 0 failed, 0 skipped
6 scenarios passed, 0 failed, 0 skipped
46 steps passed, 0 failed, 0 skipped
Took 0min 0.084s
```

### 4. リソースを削除する

```bash
terraform destroy -var-file=emulator.tfvars -auto-approve
```

---

## テストシナリオ一覧

| シナリオ | 検証内容 |
|---|---|
| VPC が正しく作成されている | CIDR・DNS ホスト名・DNS 解決 |
| プライベートサブネットが 2 つ作成されている | 各サブネットの CIDR |
| RDS 用セキュリティグループが正しく設定されている | ポート 5432/TCP インバウンドルール |
| DB サブネットグループが 2 AZ にまたがって作成されている | サブネット数 |
| DB パラメータグループが PostgreSQL 15 ファミリーで作成されている | ファミリー・パラメータ値 |
| RDS インスタンスが正しい設定で起動している | エンジン・クラス・暗号化・バックアップ等 13 項目 |

---

## ファイル構成

```
.
├── main.tf                        # VPC / Subnet / SG / RDS リソース定義
├── variables.tf                   # 変数定義
├── locals.tf                      # 共通タグ
├── outputs.tf                     # エンドポイント等の出力
├── emulator.tfvars                # エミュレーター用変数値
├── terraform.tfvars.example       # 本番環境向け変数サンプル
├── provider_emulator_override.tf  # エミュレーター向け provider 設定
├── emulator.sh                    # エミュレーター起動 + terraform ラッパー
└── features/
    ├── rds.feature                # Gherkin シナリオ
    ├── environment.py             # Behave 初期化 (boto3 クライアント)
    └── steps/
        └── rds_steps.py           # ステップ定義
```

---

## 本番 AWS への適用

エミュレーターの設定を外してそのまま本番に適用できます。

```bash
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars のパスワード等を編集

# AWS_ENDPOINT_URL などのエミュレーター向け環境変数は設定しない
terraform init
terraform apply
```

> `terraform.tfvars` は `.gitignore` により Git 管理対象外です。
