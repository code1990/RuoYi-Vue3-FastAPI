#!/usr/bin/env bash
set -euo pipefail

repo_root=$(git rev-parse --show-toplevel)
source_hook="$repo_root/scripts/hooks/pre-commit"
target_hook="$repo_root/.git/hooks/pre-commit"

if [[ ! -f "$source_hook" ]]; then
  echo "缺少 hook：$source_hook" >&2
  exit 1
fi

if [[ -e "$target_hook" ]] && ! cmp -s "$source_hook" "$target_hook"; then
  backup_hook="$target_hook.backup.$(date +%Y%m%d%H%M%S)"
  cp "$target_hook" "$backup_hook"
  echo "已备份现有 hook：$backup_hook"
fi

install -m 0755 "$source_hook" "$target_hook"
echo '已安装服务端提交范围检查。'
