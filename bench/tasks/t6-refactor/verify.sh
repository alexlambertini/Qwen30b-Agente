python3 -m unittest -q && grep -q "def _discounted" orders.py && [ "$(grep -c 'for min_qty' orders.py)" -eq 1 ] && git diff --quiet -- test_orders.py
