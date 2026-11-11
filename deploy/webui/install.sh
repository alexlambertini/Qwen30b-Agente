#!/usr/bin/env bash
# Instala/atualiza o Open WebUI em ~/webui reaproveitando a chave e a URL da config do OpenCode.
# uso: deploy/webui/install.sh [IP_DO_SERVIDOR]   (padrao: IP do Tailscale)
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; D="$HOME/webui"; IP="${1:-$(tailscale ip -4 2>/dev/null | head -1)}"
[ -n "$IP" ] || { echo "informe o IP do servidor"; exit 1; }
mkdir -p "$D/data"; chmod 700 "$D"; cp "$R/docker-compose.yml" "$D/"
if [ ! -f "$D/.env" ]; then
  K="$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.config/opencode/opencode.json")))["provider"]["qwen"]["options"]["apiKey"])')"
  umask 077
  sed -e "s#SEU_SERVIDOR#$IP#g" -e "s#^OPENAI_API_KEYS=.*#OPENAI_API_KEYS=$K;$K#" \
      -e "s#^WEBUI_SECRET_KEY=.*#WEBUI_SECRET_KEY=$(openssl rand -hex 32)#" "$R/env.example" > "$D/.env"
  echo ".env criado em $D/.env"
else
  sed -i -E "s#^OPENAI_API_BASE_URLS=.*#OPENAI_API_BASE_URLS=http://$IP:8081/v1;http://$IP:8083/v1#" "$D/.env"
  echo ".env ja existe: mantido (enderecos dos modelos atualizados para $IP)"; fi
chmod 600 "$D/.env"
cd "$D" && docker compose pull -q && docker compose up -d && docker compose ps --format '{{.Name}} {{.Status}}'
