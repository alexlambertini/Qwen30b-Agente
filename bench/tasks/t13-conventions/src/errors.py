class BankError(Exception):
    """Base dos erros de dominio."""


class InsufficientFunds(BankError):
    pass


class InvalidAmount(BankError):
    pass
