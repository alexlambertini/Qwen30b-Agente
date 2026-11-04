#!/usr/bin/env bash
# Instalador do ambiente de agentes OpenCode (Qwen3-Coder-30B) -- instala SOMENTE configuracao.
# O modelo roda no servidor remoto; aqui so ligamos o OpenCode a ele.
#
#   curl -fsSL https://raw.githubusercontent.com/alexlambertini/Qwen30b-Agente/main/install.sh | bash
#   ... | bash -s -- --url https://ia.lambertini.com.br/v1 --key SUA_CHAVE --searxng http://127.0.0.1:8888
set -euo pipefail

REPO="alexlambertini/Qwen30b-Agente"
BRANCH="${QWEN_BRANCH:-main}"
URL="${QWEN_BASE_URL:-https://ia.lambertini.com.br/v1}"
KEY="${QWEN_API_KEY:-}"
SEARX="${QWEN_SEARXNG_URL:-}"
CONF="${OPENCODE_CONFIG_DIR:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode}"
YES=0

while [ $# -gt 0 ]; do
  case "$1" in
    --url) URL="$2"; shift 2;;
    --key) KEY="$2"; shift 2;;
    --searxng) SEARX="$2"; shift 2;;
    --dir) CONF="$2"; shift 2;;
    --yes|-y) YES=1; shift;;
    -h|--help) sed -n '2,7p' "$0" 2>/dev/null || true; exit 0;;
    *) echo "Opcao desconhecida: $1" >&2; exit 2;;
  esac
done

say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[aviso]\033[0m %s\n' "$*" >&2; }
die() { printf '\033[1;31m[erro]\033[0m %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Comando necessario nao encontrado: $1"; }

ask() { # ask VAR "pergunta" [silencioso]
  local var="$1" prompt="$2" silent="${3:-}" val=""
  [ -r /dev/tty ] || die "Sem terminal para perguntar '$prompt'. Use --url/--key (ou variaveis QWEN_*)."
  if [ -n "$silent" ]; then read -r -s -p "$prompt" val </dev/tty; echo >/dev/tty
  else read -r -p "$prompt" val </dev/tty; fi
  printf -v "$var" '%s' "$val"
}

need curl; need tar

# --- 1. Parametros -----------------------------------------------------------
if [ -z "${QWEN_BASE_URL:-}" ] && [ "$URL" = "https://ia.lambertini.com.br/v1" ] && [ "$YES" = 0 ] && [ -r /dev/tty ]; then
  ask in "Endereco do servidor [$URL]: "; [ -n "$in" ] && URL="$in"
fi
URL="${URL%/}"
case "$URL" in http://*|https://*) ;; *) die "URL invalida: $URL (use http(s)://.../v1)";; esac
[ -n "$KEY" ] || ask KEY "API key do servidor (nao aparece na tela): " silent
[ -n "$KEY" ] || die "API key vazia."

if [ -z "$SEARX" ] && [ "$YES" = 0 ] && [ -r /dev/tty ]; then
  ask SEARX "URL do SearXNG para pesquisa web (ENTER para pular): "
fi

# --- 2. Validar o servidor (nao grava nada antes disso) -----------------------
say "Testando $URL/models ..."
code=$(curl -s -o /dev/null -m 15 -w '%{http_code}' -H "Authorization: Bearer $KEY" "$URL/models" || true)
case "$code" in
  200) say "Servidor respondeu 200 (chave valida).";;
  401|403) die "Servidor recusou a chave (HTTP $code). Nada foi alterado.";;
  *) warn "Servidor respondeu HTTP '$code'. Continuando mesmo assim (verifique a URL depois).";;
esac

# --- 3. Obter arquivos --------------------------------------------------------
SRC=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "$(dirname "${BASH_SOURCE[0]}")/templates/opencode.json.tpl" ]; then
  SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  say "Baixando templates de github.com/$REPO ($BRANCH) ..."
  curl -fsSL "https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz" | tar -xz -C "$TMP" --strip-components=1
  SRC="$TMP"
fi
[ -f "$SRC/templates/opencode.json.tpl" ] || die "Templates nao encontrados em $SRC"

# --- 4. Backup ----------------------------------------------------------------
mkdir -p "$CONF"
TS="$(date +%Y%m%d-%H%M%S)"
BK="$CONF/backup-$TS"
for f in opencode.json AGENTS.md agents/build.md agents/plan.md agents/reviewer.md agents/explore.md; do
  if [ -e "$CONF/$f" ]; then mkdir -p "$BK/$(dirname "$f")"; mv "$CONF/$f" "$BK/$f"; fi
done
[ -d "$BK" ] && say "Backup da configuracao anterior em $BK" || true

# --- 5. Instalar --------------------------------------------------------------
mkdir -p "$CONF/prompts" "$CONF/memory-template"
cp "$SRC"/templates/prompts/*.md "$CONF/prompts/"
cp "$SRC/templates/AGENTS.md" "$CONF/AGENTS.md"
cp -r "$SRC"/templates/memory/. "$CONF/memory-template/"

export Q_URL="$URL" Q_KEY="$KEY" Q_SEARX="$SEARX" Q_TPL="$SRC/templates/opencode.json.tpl" Q_OUT="$CONF/opencode.json"
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import json, os
c = json.load(open(os.environ["Q_TPL"]))
o = c["provider"]["qwen"]["options"]
o["baseURL"] = os.environ["Q_URL"]; o["apiKey"] = os.environ["Q_KEY"]
s = os.environ.get("Q_SEARX", "").strip()
if s:
    c["mcp"] = {"searxng": {"type": "local", "command": ["npx", "-y", "mcp-searxng"],
                            "environment": {"SEARXNG_URL": s}, "enabled": True}}
json.dump(c, open(os.environ["Q_OUT"], "w"), indent=2, ensure_ascii=False)
PY
else
  [ -z "$SEARX" ] || warn "python3 ausente: SearXNG nao configurado (instale python3 e rode de novo)."
  esc() { printf '%s' "$1" | sed -e 's/[\\&#]/\\&/g'; }
  sed -e "s#__BASE_URL__#$(esc "$URL")#" -e "s#__API_KEY__#$(esc "$KEY")#" "$SRC/templates/opencode.json.tpl" > "$CONF/opencode.json"
fi
chmod 600 "$CONF/opencode.json"

# comando auxiliar para criar a memoria do projeto
BIN="${HOME}/.local/bin"; mkdir -p "$BIN"
cat > "$BIN/qwen-agente-init" <<INIT
#!/usr/bin/env bash
# Cria .opencode/memory/ no diretorio atual a partir do template.
set -e
D="\${1:-.}/.opencode"
[ -e "\$D/memory" ] && { echo "\$D/memory ja existe; nada feito."; exit 0; }
mkdir -p "\$D" && cp -r "$CONF/memory-template" "\$D/memory" && echo "Memoria criada em \$D/memory"
INIT
chmod +x "$BIN/qwen-agente-init"

# --- 6. Verificacao -----------------------------------------------------------
if command -v python3 >/dev/null 2>&1; then python3 -c "import json;json.load(open('$CONF/opencode.json'))" && say "opencode.json valido."; fi
if command -v opencode >/dev/null 2>&1; then say "OpenCode encontrado: $(opencode --version 2>/dev/null | head -1)"
elif [ -x "$HOME/.opencode/bin/opencode" ]; then say "OpenCode encontrado: $("$HOME/.opencode/bin/opencode" --version 2>/dev/null | head -1) (em ~/.opencode/bin)"
else warn "OpenCode nao esta instalado/no PATH. Este instalador so cria a configuracao; instale o OpenCode a parte."; fi

say "Pronto. Configuracao em $CONF"
echo "  Agentes: build (padrao), plan (somente leitura), reviewer (sem editar/Bash), explore (somente leitura)"
echo "  Modelo : qwen/qwen3-coder-30b-a3b @ $URL"
echo "  Memoria de projeto: rode 'qwen-agente-init' na raiz do projeto (adicione $BIN ao PATH se preciso)."
