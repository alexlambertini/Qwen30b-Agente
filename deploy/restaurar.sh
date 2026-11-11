#!/usr/bin/env bash
# Restaura um backup do deploy/backup.sh em um servidor novo, ANTES de rodar deploy/instalar-servidor.sh.
# uso: deploy/restaurar.sh ia-backup-....tgz
set -euo pipefail
ARQ="$(realpath "$1")"; [ -f "$ARQ" ] || { echo "arquivo nao encontrado"; exit 1; }
if [ -d "$HOME/webui/data" ] && [ -n "$(ls -A "$HOME/webui/data" 2>/dev/null)" ]; then
  echo "ja existe $HOME/webui/data com conteudo; pare o Open WebUI e mova essa pasta antes de restaurar."; exit 1; fi
umask 077; tar -C "$HOME" -xzf "$ARQ"
echo "restaurado em $HOME. Agora rode: deploy/instalar-servidor.sh"
echo "Se o IP do servidor mudou, nao precisa editar nada: o instalador regrava os enderecos dos modelos."
