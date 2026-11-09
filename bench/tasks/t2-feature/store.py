class Store:
    def __init__(self):
        self.items = []
    def add(self, name, price, category):
        self.items.append({"name": name, "price": price, "category": category})
    def count(self):
        return len(self.items)
