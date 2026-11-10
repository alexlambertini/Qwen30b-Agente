python3 - <<'PY'
import unicodedata
h = "".join(c for c in unicodedata.normalize("NFD", open("index.html", encoding="utf-8").read()) if unicodedata.category(c) != "Mn")
for t in ("Oficina do Joao", "Revisao completa", "R$ 250", "Alinhamento", "R$ 120", "Servicos", "Precos", "Contato", "Seu telefone"):
    assert t.lower() in h.lower(), "texto removido: " + t
assert h.lower().count("agendar") >= 2, "botoes Agendar removidos"
PY
[ $? -eq 0 ] && "$HOME/.local/bin/qwen-layout" index.html
