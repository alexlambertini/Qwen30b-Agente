python3 - <<'PY'
import re
h = open("index.html", encoding="utf-8").read()
import unicodedata
norm = lambda t: "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()
low = norm(h)
assert "<h1" in low and "cafe aurora" in low, "sem h1 Cafe Aurora"
assert len(re.findall(r"<article", low)) >= 3, "menos de 3 article"
for campo, alt in (("nome", "name"), ("email", "email"), ("mensagem", "message")):
    assert re.search(r'<(input|textarea)[^>]*(name|id)="(%s|%s)"' % (campo, alt), low), "campo " + campo
assert "ver cardapio" in low and "enviar" in low, "botoes"
assert "<nav" in low and "<footer" in low and "<form" in low
assert "prefers-color-scheme: dark" in low, "sem modo escuro"
assert "<script src" not in low and "<link rel=\"stylesheet\"" not in low, "recurso externo"
PY
[ $? -eq 0 ] && "$HOME/.local/bin/qwen-layout" index.html
