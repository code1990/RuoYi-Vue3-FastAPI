#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${BACKEND_DIR:-${PROJECT_DIR}/ruoyi-fastapi-backend}"
PYTHON="${PYTHON:-/root/.venv/bin/python}"
SERVICE_NAME="${SERVICE_NAME:-ruoyi-fastapi.service}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:9099/transport/crypto/frontend-config}"

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

[[ -f "${BACKEND_DIR}/requirements.txt" ]] || fail "未找到后端目录: ${BACKEND_DIR}"
[[ -x "${PYTHON}" ]] || fail "Python 不可执行: ${PYTHON}"
command -v systemctl >/dev/null || fail '未安装 systemctl'
command -v curl >/dev/null || fail '未安装 curl'

cd "${PROJECT_DIR}"
git pull --ff-only origin master
"${PYTHON}" -m pip install -r "${BACKEND_DIR}/requirements.txt"
systemctl restart "${SERVICE_NAME}"
systemctl is-active --quiet "${SERVICE_NAME}" || fail "服务未运行: ${SERVICE_NAME}"
curl -fsS --max-time 10 "${HEALTH_URL}" | grep -q '"code":200' || fail "健康检查失败: ${HEALTH_URL}"
printf '后端部署完成\n'
