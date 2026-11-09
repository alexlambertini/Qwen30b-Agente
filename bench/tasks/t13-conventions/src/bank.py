from errors import InsufficientFunds, InvalidAmount


class Account:
    def __init__(self, owner: str, balance: int = 0) -> None:
        self.owner = owner
        self.balance = balance

    def deposit(self, amount: int) -> int:
        if amount <= 0:
            raise InvalidAmount(amount)
        self.balance += amount
        return self.balance

    def withdraw(self, amount: int) -> int:
        if amount <= 0:
            raise InvalidAmount(amount)
        if amount > self.balance:
            raise InsufficientFunds(amount)
        self.balance -= amount
        return self.balance
