#!/usr/bin/env bash
# Troca o modelo de codigo. uso (no servidor): ./apply-coder.sh q5 [TS=24,3] [CTX=65536] | ./apply-coder.sh q4 (volta ao original). Faz backup; se nao subir, restaura.
set -e
U=/etc/systemd/system/llama-opencode.service; D="$(dirname "$0")"
MODE=${1:?q5|q4}; TS=${2:-24,3}; CTX=${3:-65536}
KEY=$(grep -oP -- '--api-key \K\S+' $U)
if [ "$MODE" = q4 ]; then B=$(ls -t $U.q4orig 2>/dev/null | head -1); [ -n "$B" ] || { echo "sem backup q4orig"; exit 1; }; sudo cp $U.q4orig $U
else
  [ -f $U.q4orig ] || sudo cp $U $U.q4orig
  sudo cp $U /tmp/prev.unit
  sed -e "s|@@KEY@@|$KEY|" -e "s|@@TS@@|$TS|" -e "s|@@CTX@@|$CTX|" $D/llama-opencode-q5.service.tpl | sudo tee $U >/dev/null
fi
sudo systemctl daemon-reload; sudo systemctl restart llama-opencode
for i in $(seq 150); do curl -fs -H "Authorization: Bearer $KEY" http://100.94.64.97:8081/health >/dev/null && { echo "coder $MODE OK (ts=$TS ctx=$CTX)"; nvidia-smi --query-gpu=index,memory.used --format=csv,noheader; exit 0; }; sleep 3; done
echo "NAO subiu: restaurando Q4"; sudo cp $U.q4orig $U; sudo systemctl daemon-reload; sudo systemctl restart llama-opencode; exit 1
