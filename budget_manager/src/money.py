from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

CENT = Decimal("0.01")


def quantize_amount(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def parse_amount(raw: str) -> Decimal:
    cleaned = raw.strip().replace("$", "")
    if cleaned == "":
        raise ValueError("Amount is required.")
    try:
        value = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError("Invalid amount format.") from exc
    if value < 0:
        raise ValueError("Amount must be non-negative.")
    return quantize_amount(value)


def decimal_to_str(value: Decimal) -> str:
    return f"{quantize_amount(value):.2f}"


def str_to_decimal(value: str) -> Decimal:
    return quantize_amount(Decimal(value))
