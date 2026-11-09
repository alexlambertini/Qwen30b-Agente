python3 -m unittest -q 2>&1 && python3 - <<'PY'
import io, contextlib, re
from repo import InMemoryRepo
from service import InventoryService
from models import Item
import cli
assert Item("x").min_stock == 0
s = InventoryService(InMemoryRepo())
s.add_item("zinco", 1, 1.0, min_stock=5)
s.add_item("aco", 2, 1.0, min_stock=3)
s.add_item("ok", 9, 1.0, min_stock=3)
s.add_item("semmin", 0)
assert [i.name for i in s.low_stock()] == ["aco", "zinco"], s.low_stock()
try:
    s.remove_stock("aco", 3); raise SystemExit("deveria levantar ValueError")
except ValueError: pass
assert s.repo.get("aco").quantity == 2
assert s.remove_stock("aco", 2).quantity == 0
cli.main(["add", "cobre", "--qty", "1", "--min", "4"], s)
b = io.StringIO()
with contextlib.redirect_stdout(b): cli.main(["low"], s)
assert b.getvalue().split() == ["aco", "cobre", "zinco"], b.getvalue()
b = io.StringIO()
with contextlib.redirect_stdout(b): cli.main(["list"], s)
assert "ok\t9" in b.getvalue()
import glob
n = sum(len(re.findall(r"def test", open(f).read())) for f in glob.glob("test*.py") + glob.glob("tests/test*.py"))
assert n >= 4, f"poucos testes: {n}"
PY
