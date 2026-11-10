#!/usr/bin/env bash
# Monta uma config ISOLADA a partir de templates/ (sem tocar ~/.config/opencode) para usar com: bench/run.sh -x DIR
# uso: bench/mkconf.sh DIR [baseURL] [apiKey]   (padrao: URL e chave da config instalada)
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"; D="$1/opencode"
rm -rf "$D"; mkdir -p "$D/prompts"
cp "$R"/templates/prompts/*.md "$D/prompts/"; mkdir -p "$HOME/.local/bin"; cp "$R/templates/bin/qwen-imagem" "$R/templates/bin/qwen-layout" "$HOME/.local/bin/"; cp "$R/templates/AGENTS.md" "$D/"
Q_TPL="$R/templates/opencode.json.tpl" Q_OUT="$D/opencode.json" Q_URL="${2:-}" Q_KEY="${3:-}" python3 - <<'PY'
import json, os
c = json.load(open(os.environ["Q_TPL"]))
o = c["provider"]["qwen"]["options"]
live = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), "opencode", "opencode.json")
lo = json.load(open(live))["provider"]["qwen"]["options"] if os.path.exists(live) else {}
o["baseURL"] = os.environ["Q_URL"] or lo["baseURL"]; o["apiKey"] = os.environ["Q_KEY"] or lo["apiKey"]
json.dump(c, open(os.environ["Q_OUT"], "w"), indent=2, ensure_ascii=False)
PY
chmod 600 "$D/opencode.json"; echo "config de teste em $D"
