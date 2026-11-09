from models import Item
from repo import InMemoryRepo


class InventoryService:
    def __init__(self, repo: InMemoryRepo):
        self.repo = repo

    def add_item(self, name: str, quantity: int = 0, price: float = 0.0) -> Item:
        item = Item(name=name, quantity=quantity, price=price)
        self.repo.save(item)
        return item

    def remove_stock(self, name: str, amount: int) -> Item:
        item = self.repo.get(name)
        item.quantity -= amount
        self.repo.save(item)
        return item

    def total_value(self) -> float:
        return sum(i.quantity * i.price for i in self.repo.all())
