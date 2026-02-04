from __future__ import annotations

from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import List

from .money import quantize_amount


def weekly_income_simple(monthly_income: Decimal) -> Decimal:
    return quantize_amount(monthly_income / Decimal("4"))


def weekly_income_average(monthly_income: Decimal) -> Decimal:
    return quantize_amount(monthly_income / Decimal("4.345"))


def days_in_month(target_month: str) -> int:
    year, month = map(int, target_month.split("-"))
    return monthrange(year, month)[1]


def daily_discretionary_schedule(
    target_month: str, discretionary_income: Decimal
) -> List[Decimal]:
    total_days = days_in_month(target_month)
    if total_days <= 0:
        return []
    base = (discretionary_income / Decimal(total_days)).quantize(
        Decimal("0.01")
    )
    schedule = [base for _ in range(total_days)]
    scheduled_total = sum(schedule, Decimal("0.00"))
    remainder = quantize_amount(discretionary_income - scheduled_total)
    cents = int((remainder * 100).to_integral_value())
    index = 0
    while cents > 0:
        schedule[index] = quantize_amount(schedule[index] + Decimal("0.01"))
        cents -= 1
        index = (index + 1) % total_days
    return schedule


def daily_schedule_with_dates(target_month: str, schedule: List[Decimal]) -> List[tuple[date, Decimal]]:
    year, month = map(int, target_month.split("-"))
    return [
        (date(year, month, day + 1), amount) for day, amount in enumerate(schedule)
    ]
