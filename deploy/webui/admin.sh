#!/usr/bin/env bash
# Cria o administrador do Open WebUI na primeira vez (senha aleatoria em ~/webui/admin.txt, 600)
# e renova o token usado pelo webui/configurar.py (~/webui/.token). Nao imprime senha nem token.
set -euo pipefail
D="$HOME/webui"; U="${1:-http://127.0.0.1:3000}"; EMAIL="${WEBUI_ADMIN_EMAIL:-admin@ia.local}"
umask 077
novo=0
if [ ! -f "$D/admin.txt" ]; then
  P="$(openssl rand -base64 24 | tr -d '/+=' | cut -c1-20)"
  printf 'usuario: %s\nsenha: %s\n' "$EMAIL" "$P" > "$D/admin.txt"; novo=1
fi
EMAIL="$(sed -n 's/^usuario: //p' "$D/admin.txt")"; P="$(sed -n 's/^senha: //p' "$D/admin.txt")"
corpo() { python3 -c 'import json,sys; print(json.dumps({"name":"Administrador","email":sys.argv[1],"password":sys.argv[2]}))' "$EMAIL" "$P"; }
pedir() { curl -s -m 30 -X POST "$U/api/v1/auths/$1" -H "Content-Type: application/json" -d "$(corpo)"; }
R="$(pedir signin)"
if ! printf '%s' "$R" | grep -q '"token"'; then R="$(pedir signup)"; fi
printf '%s' "$R" | python3 -c 'import json,sys,os
d=json.load(sys.stdin)
if not d.get("token"): sys.exit("falha ao entrar como admin: %s" % str(d)[:200])
open(os.path.expanduser("~/webui/.token"),"w").write(d["token"]); print("admin ok:", d.get("email"), "| papel:", d.get("role"))'
chmod 600 "$D/admin.txt" "$D/.token"
[ "$novo" = 1 ] && echo "PRIMEIRO ACESSO: usuario e senha em $D/admin.txt (troque a senha na interface)." || true
