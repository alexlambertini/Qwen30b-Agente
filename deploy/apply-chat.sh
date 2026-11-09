#!/usr/bin/env bash
# Aplica o chat com 16 slots (rode NO servidor, com sudo). Faz backup e volta atras se nao subir.
set -e
U=/etc/systemd/system/llama-chat.service
KEY=$(grep -oP -- '--api-key \K\S+' $U)
sudo cp $U $U.bak.$(date +%s)
sed "s|@@CHAT_KEY@@|$KEY|" "$(dirname "$0")/llama-chat.service.tpl" | sudo tee $U >/dev/null
sudo systemctl daemon-reload && sudo systemctl restart llama-chat
for i in $(seq 40); do curl -fs -H "Authorization: Bearer $KEY" http://100.94.64.97:8083/health >/dev/null && { echo "chat OK"; python3 "$(dirname "$0")/loadtest.py" http://100.94.64.97:8083 "$KEY" 20; exit 0; }; sleep 3; done
echo "NAO subiu: restaurando"; sudo cp $(ls -t $U.bak.* | head -1) $U; sudo systemctl daemon-reload; sudo systemctl restart llama-chat; exit 1
