python3 -m unittest -q 2>&1 && python3 - <<'PY'
from ratelimit import SlidingWindowLimiter as L
t = [0.0]
l = L(2, 10, clock=lambda: t[0])
assert l.allow("a") and l.retry_after("a") == 0.0
t[0] = 4; assert l.allow("a")
assert not l.allow("a") and not l.allow("a")
assert abs(l.retry_after("a") - 6) < 1e-9, l.retry_after("a")
assert l.allow("b")
t[0] = 9.999; assert not l.allow("a")
t[0] = 10; assert l.retry_after("a") == 0.0 and l.allow("a")
assert not l.allow("a"); assert abs(l.retry_after("a") - 4) < 1e-9
t[0] = 14; assert l.allow("a")
for bad in [(0, 1), (1, 0), (-1, 5)]:
    try: L(*bad); raise SystemExit("sem ValueError")
    except ValueError: pass
l = L(3, 1, clock=lambda: t[0])
for i in range(5000):
    t[0] += 0.5; l.allow("k")
import sys
sizes = [len(v) for v in vars(l).values() if hasattr(v, "get") and v.get("k") is not None for v in [v["k"]] if hasattr(v, "__len__")]
assert sizes and max(sizes) <= 10, f"memoria cresce: {sizes}"
PY
