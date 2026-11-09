"""Handlers de eventos financeiros. Cada handler valida o payload e devolve um lancamento."""


class ValidationError(ValueError):
    pass


def _base(kind, payload):
    return {"kind": kind, "account": payload["account"], "amount": payload["amount"], "currency": payload.get("currency", "BRL")}


def handle_payment(payload):
    """Processa um evento do tipo payment."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("payment", payload)
    entry["sign"] = 1
    return entry


def handle_refund(payload):
    """Processa um evento do tipo refund."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    entry = _base("refund", payload)
    entry["sign"] = -1
    return entry


def handle_chargeback(payload):
    """Processa um evento do tipo chargeback."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    entry = _base("chargeback", payload)
    entry["sign"] = -1
    return entry


def handle_payout(payload):
    """Processa um evento do tipo payout."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("payout", payload)
    entry["sign"] = -1
    return entry


def handle_transfer(payload):
    """Processa um evento do tipo transfer."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("transfer", payload)
    entry["sign"] = 1
    return entry


def handle_deposit(payload):
    """Processa um evento do tipo deposit."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("deposit", payload)
    entry["sign"] = 1
    return entry


def handle_withdrawal(payload):
    """Processa um evento do tipo withdrawal."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("withdrawal", payload)
    entry["sign"] = -1
    return entry


def handle_fee(payload):
    """Processa um evento do tipo fee."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("fee", payload)
    entry["sign"] = -1
    return entry


def handle_adjustment(payload):
    """Processa um evento do tipo adjustment."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("adjustment", payload)
    entry["sign"] = 1
    return entry


def handle_reversal(payload):
    """Processa um evento do tipo reversal."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    entry = _base("reversal", payload)
    entry["sign"] = -1
    return entry


def handle_invoice(payload):
    """Processa um evento do tipo invoice."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("invoice", payload)
    entry["sign"] = 1
    return entry


def handle_credit_note(payload):
    """Processa um evento do tipo credit_note."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("credit_note", payload)
    entry["sign"] = 1
    return entry


def handle_subscription(payload):
    """Processa um evento do tipo subscription."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("subscription", payload)
    entry["sign"] = 1
    return entry


def handle_renewal(payload):
    """Processa um evento do tipo renewal."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("renewal", payload)
    entry["sign"] = 1
    return entry


def handle_cancellation(payload):
    """Processa um evento do tipo cancellation."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("cancellation", payload)
    entry["sign"] = 1
    return entry


def handle_trial(payload):
    """Processa um evento do tipo trial."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("trial", payload)
    entry["sign"] = 1
    return entry


def handle_upgrade(payload):
    """Processa um evento do tipo upgrade."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("upgrade", payload)
    entry["sign"] = 1
    return entry


def handle_downgrade(payload):
    """Processa um evento do tipo downgrade."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("downgrade", payload)
    entry["sign"] = 1
    return entry


def handle_coupon(payload):
    """Processa um evento do tipo coupon."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("coupon", payload)
    entry["sign"] = 1
    return entry


def handle_gift(payload):
    """Processa um evento do tipo gift."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("gift", payload)
    entry["sign"] = 1
    return entry


def handle_topup(payload):
    """Processa um evento do tipo topup."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("topup", payload)
    entry["sign"] = 1
    return entry


def handle_hold(payload):
    """Processa um evento do tipo hold."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("hold", payload)
    entry["sign"] = 1
    return entry


def handle_release(payload):
    """Processa um evento do tipo release."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("release", payload)
    entry["sign"] = 1
    return entry


def handle_capture(payload):
    """Processa um evento do tipo capture."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("capture", payload)
    entry["sign"] = 1
    return entry


def handle_void(payload):
    """Processa um evento do tipo void."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("void", payload)
    entry["sign"] = -1
    return entry


def handle_dispute(payload):
    """Processa um evento do tipo dispute."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("dispute", payload)
    entry["sign"] = 1
    return entry


def handle_settlement(payload):
    """Processa um evento do tipo settlement."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("settlement", payload)
    entry["sign"] = 1
    return entry


def handle_tax(payload):
    """Processa um evento do tipo tax."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("tax", payload)
    entry["sign"] = -1
    return entry


def handle_tip(payload):
    """Processa um evento do tipo tip."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("tip", payload)
    entry["sign"] = 1
    return entry


def handle_cashback(payload):
    """Processa um evento do tipo cashback."""
    if "account" not in payload:
        raise ValidationError("account is required")
    if "amount" not in payload:
        raise ValidationError("amount is required")
    if payload["amount"] <= 0:
        raise ValidationError("amount must be positive")
    entry = _base("cashback", payload)
    entry["sign"] = 1
    return entry


HANDLERS = {
    "payment": handle_payment,
    "refund": handle_refund,
    "chargeback": handle_chargeback,
    "payout": handle_payout,
    "transfer": handle_transfer,
    "deposit": handle_deposit,
    "withdrawal": handle_withdrawal,
    "fee": handle_fee,
    "adjustment": handle_adjustment,
    "reversal": handle_reversal,
    "invoice": handle_invoice,
    "credit_note": handle_credit_note,
    "subscription": handle_subscription,
    "renewal": handle_renewal,
    "cancellation": handle_cancellation,
    "trial": handle_trial,
    "upgrade": handle_upgrade,
    "downgrade": handle_downgrade,
    "coupon": handle_coupon,
    "gift": handle_gift,
    "topup": handle_topup,
    "hold": handle_hold,
    "release": handle_release,
    "capture": handle_capture,
    "void": handle_void,
    "dispute": handle_dispute,
    "settlement": handle_settlement,
    "tax": handle_tax,
    "tip": handle_tip,
    "cashback": handle_cashback,
}


def dispatch(kind, payload):
    return HANDLERS[kind](payload)
