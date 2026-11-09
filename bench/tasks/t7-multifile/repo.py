from models import Item


class InMemoryRepo:
    def __init__(self):
        self._items = {}

    def save(self, item: Item) -> None:
        self._items[item.name] = item

    def get(self, name: str) -> Item:
        return self._items[name]

    def all(self) -> list[Item]:
        return list(self._items.values())
