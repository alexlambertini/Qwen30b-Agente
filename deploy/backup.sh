#!/usr/bin/env bash
# Backup do que NAO esta no git: conversas/usuarios do Open WebUI, casos juridicos, chaves e config do OpenCode.
# uso: deploy/backup.sh [PASTA_DESTINO]   -> gera ia-backup-AAAAMMDD-HHMMSS.tgz (permissao 600). CONTEM SEGREDOS E DADOS DE CLIENTE.
set -euo pipefail
DEST="${1:-$HOME/backups}"; mkdir -p "$DEST"; chmod 700 "$DEST"
ARQ="$DEST/ia-backup-$(date +%Y%m%d-%H%M%S).tgz"
itens=(); for i in webui/data webui/.env webui/admin.txt revisor/casos revisor/chave searxng/settings.yml .config/opencode; do
  [ -e "$HOME/$i" ] && itens+=("$i"); done
umask 077
# os dados do Open WebUI pertencem ao root do container: le por dentro do docker quando preciso
if tar -C "$HOME" -czf "$ARQ" --exclude='webui/data/cache' "${itens[@]}" 2>/dev/null; then :; else
  docker run --rm -v "$HOME:/h:ro" -v "$DEST:/o" alpine tar -C /h -czf "/o/$(basename "$ARQ")" --exclude='webui/data/cache' "${itens[@]}"
  docker run --rm -v "$DEST:/o" alpine chown "$(id -u):$(id -g)" "/o/$(basename "$ARQ")"
fi
chmod 600 "$ARQ"; echo "backup: $ARQ ($(du -h "$ARQ" | cut -f1))"
