#!/usr/bin/env bash
# Instala o servidor de ferramentas do ADVOGADO REVISIONAL como servico do usuario (systemd --user).
# uso: deploy/revisor/install.sh [IP_DE_ESCUTA] [PORTA]
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"; B="$HOME/revisor"; IP="${1:-$(tailscale ip -4 2>/dev/null | head -1)}"; PORTA="${2:-8890}"
mkdir -p "$B/casos"; chmod 700 "$B" "$B/casos"
[ -d "$B/nucleo" ] || git clone -q https://github.com/alexlambertini/advogado-revisional "$B/nucleo"
[ -d "$B/venv" ] || python3 -m venv "$B/venv"
"$B/venv/bin/pip" -q install pypdf python-docx openpyxl pytesseract Pillow fastapi "uvicorn[standard]"
cp "$R/servidor.py" "$B/servidor.py"
[ -f "$B/chave" ] || ( umask 077; openssl rand -hex 32 > "$B/chave" )
chmod 600 "$B/chave"
mkdir -p "$HOME/.config/systemd/user"
cat > "$HOME/.config/systemd/user/revisor-tools.service" <<U
[Unit]
Description=Servidor de ferramentas do ADVOGADO REVISIONAL (Open WebUI)
After=network-online.target

[Service]
WorkingDirectory=$B
Environment=REVISOR_NUCLEO=$B/nucleo REVISOR_CASOS=$B/casos REVISOR_UPLOADS=$HOME/webui/data/uploads REVISOR_CHAVE=$B/chave
ExecStart=$B/venv/bin/uvicorn servidor:app --host $IP --port $PORTA --no-access-log
Restart=on-failure
RestartSec=5
MemoryMax=1G
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=default.target
U
systemctl --user daemon-reload
systemctl --user enable --now revisor-tools.service
systemctl --user restart revisor-tools.service
sleep 2; systemctl --user is-active revisor-tools.service
echo "servidor em http://$IP:$PORTA  (chave em $B/chave)"
loginctl show-user "$USER" -p Linger 2>/dev/null || true
