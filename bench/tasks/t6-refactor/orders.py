RETAIL_TIERS = [(100, 0.15), (50, 0.10), (10, 0.05)]
WHOLESALE_TIERS = [(500, 0.30), (200, 0.20)]

def price_retail(base, qty):
    rate = 0
    for min_qty, r in RETAIL_TIERS:
        if qty >= min_qty:
            rate = r
            break
    return round(base * qty * (1 - rate), 2)

def price_wholesale(base, qty):
    rate = 0
    for min_qty, r in WHOLESALE_TIERS:
        if qty >= min_qty:
            rate = r
            break
    return round(base * qty * (1 - rate) * 0.9, 2)
