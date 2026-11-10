python3 - <<'PY'
import re
import unicodedata
h = "".join(c for c in unicodedata.normalize("NFD", open("cadastro.html", encoding="utf-8").read()) if unicodedata.category(c) != "Mn"); low = h.lower()
assert len(re.findall(r"<label", low)) >= 4, "labels"
for t in ("email", "password"):
    assert 'type="%s"' % t in low, "type " + t
assert low.count("required") >= 4, "required"
assert "autocomplete=" in low and 'aria-live="polite"' in low and "minlength=\"8\"" in low.replace("'", '"') or "length < 8" in low or "length<8" in low, "validacao/aria-live"
assert "alert(" not in low, "usou alert"
assert "criar conta" in low and "addeventlistener" in low
PY
[ $? -eq 0 ] && "$HOME/.local/bin/qwen-layout" cadastro.html
