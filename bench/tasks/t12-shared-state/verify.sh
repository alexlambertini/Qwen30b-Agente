python3 -m unittest -q 2>&1 && python3 - <<'PY'
import re
from cart import Cart
a, b = Cart("a"), Cart("b")
a.add("x", 10); a.apply_coupon("C", 50)
assert b.items == [] and b.total() == 0 and b.coupons == {}
b.add("y", 20)
assert a.total() == 5 and b.total() == 20
assert a.items[0]["tags"] == ["cart"] and b.items[0]["tags"] == ["cart"], (a.items, b.items)
t = ["promo"]; b.add("z", 1, t); assert b.items[1]["tags"].count("cart") == 1 and "promo" in b.items[1]["tags"]
import glob
assert sum(len(re.findall(r"def test", open(f).read())) for f in glob.glob("test*.py") + glob.glob("tests/test*.py")) >= 4, "faltam testes"
PY
