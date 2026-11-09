from pricing import apply_discount
def total(items, discount=0):
    s = sum(i["price"] * i["qty"] for i in items)
    return round(apply_discount(s, discount), 2)
