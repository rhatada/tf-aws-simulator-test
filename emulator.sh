#!/usr/bin/env bash
# AWS Emulator に向けて Terraform を実行するラッパースクリプト
# 使い方:
#   ./emulator.sh init
#   ./emulator.sh plan
#   ./emulator.sh apply
#   ./emulator.sh destroy

set -euo pipefail

EMULATOR_PORT=9297
EMULATOR_PID_FILE="/tmp/aws-emulator.pid"
EMULATOR_BIN="/home/rhatada/Desktop/project/jal/aws-emulator-src/target/debug/aws-emulator"
CA_BUNDLE="$HOME/.aws/emulator/${EMULATOR_PORT}/ca.pem"

# --- エミュレーターが起動していなければ起動 ---
if ! curl -sk "https://127.0.0.1:${EMULATOR_PORT}/__admin/health" | grep -q "ok" 2>/dev/null; then
  echo "[emulator] Starting AWS Emulator on port ${EMULATOR_PORT}..."
  "$EMULATOR_BIN" --port "$EMULATOR_PORT" --telemetry off &
  echo $! > "$EMULATOR_PID_FILE"
  sleep 3
  echo "[emulator] Started (PID=$(cat $EMULATOR_PID_FILE))"
else
  echo "[emulator] Already running on port ${EMULATOR_PORT}"
fi

# --- 環境変数をエミュレーターへ向ける ---
export AWS_CA_BUNDLE="$CA_BUNDLE"
export AWS_ENDPOINT_URL="https://127.0.0.1:${EMULATOR_PORT}"

# プロバイダーオーバーライドを有効化
cp provider_emulator_override.tf _active_emulator_override.tf.bak 2>/dev/null || true

# --- Terraform 実行 ---
CMD="${1:-plan}"
shift || true

echo "[terraform] Running: terraform $CMD -var-file=emulator.tfvars $*"
terraform "$CMD" -var-file=emulator.tfvars "$@"
