python3 -m unittest -q 2>&1 && python3 - <<'PY'
import subprocess, re
from handlers import HANDLERS, ValidationError, dispatch
for k in HANDLERS:
    for bad in (0, -3):
        try: dispatch(k, {"account": "a", "amount": bad}); raise SystemExit(f"{k} aceitou {bad}")
        except ValidationError as e: assert str(e) == "amount must be positive", (k, str(e))
    e = dispatch(k, {"account": "a", "amount": 2}); assert e["kind"] == k and e["amount"] == 2
assert dispatch("refund", {"account": "a", "amount": 2})["sign"] == -1 and dispatch("gift", {"account": "a", "amount": 2})["sign"] == 1
st = subprocess.run(["git", "diff", "--numstat", "--", "handlers.py"], capture_output=True, text=True).stdout.split()
assert int(st[0]) <= 12 and int(st[1]) <= 3, f"diff grande demais em handlers.py: +{st[0]} -{st[1]}"
t = open("test_handlers.py").read()
assert all(w in t for w in ("refund", "chargeback", "reversal")), "testes nao cobrem os 3 handlers"
PY
