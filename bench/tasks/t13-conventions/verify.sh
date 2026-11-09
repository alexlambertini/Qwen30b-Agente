python3 -m unittest discover -s tests -q 2>&1 && ! grep -rn "print(" src/ && python3 - <<'PY'
import sys, inspect, re
sys.path.insert(0, "src")
import bank, errors
from bank import Account, transfer
assert issubclass(errors.SameAccount, errors.BankError)
a, b = Account("a", 100), Account("b", 5)
assert transfer(a, b, 30) == 70 and b.balance == 35
for amt, exc in ((71, errors.InsufficientFunds), (0, errors.InvalidAmount), (-5, errors.InvalidAmount)):
    try: transfer(a, b, amt); raise SystemExit(f"sem erro para {amt}")
    except exc: pass
    assert (a.balance, b.balance) == (70, 35), "nao atomico"
try: transfer(a, a, 10); raise SystemExit("mesma conta aceita")
except errors.SameAccount: pass
assert a.balance == 70
sig = inspect.signature(transfer)
assert all(p.annotation is not inspect.Parameter.empty for p in sig.parameters.values()) and sig.return_annotation is not inspect.Signature.empty, "sem type hints"
src = open("src/bank.py").read()
assert "float" not in src and "raise ValueError" not in src and "raise Exception" not in src
t = open("tests/test_bank.py").read()
assert "transfer" in t and len(re.findall(r"def test", t)) >= 5, "testes insuficientes em tests/test_bank.py"
PY
