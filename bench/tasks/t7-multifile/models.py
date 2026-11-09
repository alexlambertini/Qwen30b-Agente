from dataclasses import dataclass


@dataclass
class Item:
    name: str
    quantity: int = 0
    price: float = 0.0
