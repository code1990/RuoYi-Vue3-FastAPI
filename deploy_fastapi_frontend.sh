#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ZIP_FILE="${ZIP_FILE:-${SCRIPT_DIR}/../ruoyi-fastapi-frontend-dist.zip}"
DEPLOY_DIR="${DEPLOY_DIR:-/usr/share/nginx/html/fastapi}"
BACKUP_ROOT="${BACKUP_ROOT:-/root/project/nginx_fastapi_backups}"
TMP_ROOT="${TMP_ROOT:-/tmp}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1/}"
API_HEALTH_URL="${API_HEALTH_URL:-http://127.0.0.1/prod-api/transport/crypto/frontend-config}"
KEEP_BACKUP="${KEEP_BACKUP:-0}"

timestamp="$(date +%Y%m%d_%H%M%S)"
tmp_dir="${TMP_ROOT%/}/fastapi_dist_${timestamp}_$$"
backup_dir="${BACKUP_ROOT%/}/fastapi_${timestamp}"
new_dir="${DEPLOY_DIR}.new_${timestamp}_$$"
old_dir="${DEPLOY_DIR}.old_${timestamp}_$$"

log() {
  printf '[%s] %s\n' "$(date '+%F %T')" "$*"
}

fail() {
  log "ERROR: $*"
  exit 1
}

cleanup_tmp() {
  rm -rf "${tmp_dir}" "${new_dir}" "${old_dir}"
}

rollback() {
  local exit_code=$?
  if [[ ${exit_code} -eq 0 ]]; then
    return
  fi

  log "部署失败，开始回滚"
  if [[ -d "${backup_dir}" ]]; then
    rm -rf "${DEPLOY_DIR}"
    mkdir -p "$(dirname "${DEPLOY_DIR}")"
    cp -a "${backup_dir}" "${DEPLOY_DIR}"
    nginx -t >/dev/null 2>&1 && reload_nginx >/dev/null 2>&1 || true
    log "已从备份回滚: ${backup_dir}"
  else
    log "未找到备份目录，无法回滚: ${backup_dir}"
  fi

  cleanup_tmp
  log "已保留部署包: ${ZIP_FILE}"
  log "已保留备份: ${backup_dir}"
  exit "${exit_code}"
}

reload_nginx() {
  if command -v systemctl >/dev/null 2>&1 && systemctl is-active --quiet nginx; then
    systemctl reload nginx
  else
    nginx -s reload
  fi
}

trap rollback ERR
trap cleanup_tmp EXIT

[[ -f "${ZIP_FILE}" ]] || fail "部署包不存在: ${ZIP_FILE}"
command -v unzip >/dev/null 2>&1 || fail "未安装 unzip"
command -v curl >/dev/null 2>&1 || fail "未安装 curl"
command -v nginx >/dev/null 2>&1 || fail "未安装 nginx"

log "检查压缩包: ${ZIP_FILE}"
unzip -tq "${ZIP_FILE}" >/dev/null

mkdir -p "${tmp_dir}" "${new_dir}" "${BACKUP_ROOT}" "$(dirname "${DEPLOY_DIR}")"

log "解压到临时目录: ${tmp_dir}"
unzip -q "${ZIP_FILE}" -d "${tmp_dir}" || [[ $? -eq 1 ]]

find "${tmp_dir}" -depth -name '*\\*' -exec bash -c '
  for path do
    target=${path//\\//}
    [ "$path" = "$target" ] || { mkdir -p "$(dirname "$target")"; mv "$path" "$target"; }
  done
' sh {} +

source_dir="${tmp_dir}"
if [[ -f "${tmp_dir}/index.html" ]]; then
  source_dir="${tmp_dir}"
elif [[ -f "${tmp_dir}/dist/index.html" ]]; then
  source_dir="${tmp_dir}/dist"
else
  first_index="$(find "${tmp_dir}" -mindepth 2 -maxdepth 3 -type f -name index.html | head -n 1 || true)"
  [[ -n "${first_index}" ]] || fail "解压后未找到 index.html，请确认 dist.zip 是否为前端构建产物"
  source_dir="$(dirname "${first_index}")"
fi

log "识别到前端目录: ${source_dir}"
cp -a "${source_dir}/." "${new_dir}/"
[[ -f "${new_dir}/index.html" ]] || fail "新版本目录缺少 index.html"

log "备份当前版本: ${backup_dir}"
if [[ -d "${DEPLOY_DIR}" ]]; then
  cp -a "${DEPLOY_DIR}" "${backup_dir}"
else
  mkdir -p "${backup_dir}"
fi

log "原子替换部署目录: ${DEPLOY_DIR}"
if [[ -e "${DEPLOY_DIR}" ]]; then
  mv "${DEPLOY_DIR}" "${old_dir}"
fi
mv "${new_dir}" "${DEPLOY_DIR}"
rm -rf "${old_dir}"

log "检查 nginx 配置"
nginx -t

log "重载 nginx"
reload_nginx

log "验证首页: ${HEALTH_URL}"
curl -fsS --max-time 10 "${HEALTH_URL}" | grep -qi '<html' || fail "首页验证失败"

log "验证后端代理: ${API_HEALTH_URL}"
curl -fsS --max-time 10 "${API_HEALTH_URL}" | grep -q '"code":200' || fail "后端代理验证失败"

if [[ "${KEEP_BACKUP}" == "1" ]]; then
  log "部署成功，按 KEEP_BACKUP=1 保留备份: ${backup_dir}"
else
  log "部署成功，删除备份: ${backup_dir}"
  rm -rf "${backup_dir}"
fi

log "删除部署包: ${ZIP_FILE}"
rm -f "${ZIP_FILE}"

log "完成"
