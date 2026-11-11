#!/usr/bin/env bash
# Sobe TUDO do lado do servidor a partir do repositorio (ver WebUI.md):
#   Open WebUI + pesquisa (SearXNG) + imagem (ComfyUI) + nucleo ADVOGADO REVISIONAL + modelos/agentes do seletor.
# Pre-requisitos (nao instalados aqui): llama-server do coder (:8081) e do chat (:8083) no ar - veja deploy/apply-coder.sh
# e deploy/apply-chat.sh -, a config do OpenCode instalada (install.sh, de onde sai a API key), Docker e, para imagem, o ComfyUI (:8188).
# uso: deploy/instalar-servidor.sh [IP_DO_SERVIDOR]     (padrao: IP do Tailscale)   | pode ser rodado de novo: atualiza.
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"; IP="${1:-$(tailscale ip -4 2>/dev/null | head -1)}"
[ -n "$IP" ] || { echo "informe o IP do servidor: $0 IP"; exit 1; }
passo() { printf '\n== %s\n' "$*"; }

passo "1/6 pacotes do sistema (OCR, PDF, conversao de .doc)"
falta=""; for b in tesseract pdftotext soffice; do command -v "$b" >/dev/null || falta="$falta $b"; done
if [ -n "$falta" ] || ! tesseract --list-langs 2>/dev/null | grep -qx por; then
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-por poppler-utils libreoffice-writer-nogui
else echo "ja instalados"; fi

passo "2/6 SearXNG (pesquisa na web)"
if curl -s -m 15 -o /dev/null "http://127.0.0.1:8888/search?q=teste&format=json"; then echo "ja responde em :8888"
else
  mkdir -p "$HOME/searxng"
  [ -f "$HOME/searxng/settings.yml" ] || cat > "$HOME/searxng/settings.yml" <<Y
use_default_settings: true
server:
  secret_key: "$(openssl rand -hex 32)"
  limiter: false
search:
  formats: [html, json]
Y
  docker rm -f searxng >/dev/null 2>&1 || true
  docker run -d --name searxng --restart unless-stopped -p 8888:8080 \
    -v "$HOME/searxng/settings.yml:/etc/searxng/settings.yml:ro" searxng/searxng:latest >/dev/null
  echo "SearXNG iniciado em :8888"
fi

passo "3/6 Open WebUI"
"$R/deploy/webui/install.sh" "$IP"
printf "aguardando o Open WebUI"; for _ in $(seq 1 90); do
  [ "$(curl -s -m 3 -o /dev/null -w '%{http_code}' http://127.0.0.1:3000/health)" = 200 ] && break; printf .; sleep 5; done; echo

passo "4/6 administrador"
"$R/deploy/webui/admin.sh"

passo "5/6 servidor de ferramentas do ADVOGADO REVISIONAL"
"$R/deploy/revisor/install.sh" "$IP"
loginctl show-user "$USER" -p Linger 2>/dev/null | grep -q yes || sudo loginctl enable-linger "$USER"
for _ in $(seq 1 20); do curl -s -m 3 -o /dev/null "http://$IP:8890/openapi.json" && break; sleep 2; done

passo "6/6 ferramentas, agentes e imagem no Open WebUI"
python3 "$R/webui/configurar.py"

cat <<F

PRONTO. Open WebUI em http://127.0.0.1:3000 (publique por tunel/proxy com HTTPS).
Login do administrador: $HOME/webui/admin.txt
Backup dos dados: deploy/backup.sh   |   Restaurar em outro servidor: deploy/restaurar.sh ARQUIVO.tgz
F
