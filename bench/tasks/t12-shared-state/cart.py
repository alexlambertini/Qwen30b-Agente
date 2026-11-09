class Cart:
    items = []
    coupons = {}

    def __init__(self, customer):
        self.customer = customer

    def add(self, name, price, tags=[]):
        tags.append("cart")
        self.items.append({"name": name, "price": price, "tags": tags})

    def apply_coupon(self, code, percent):
        self.coupons[code] = percent

    def total(self):
        subtotal = sum(i["price"] for i in self.items)
        discount = sum(self.coupons.values())
        return round(subtotal * (1 - discount / 100), 2)
