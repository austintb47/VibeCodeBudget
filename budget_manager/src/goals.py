from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from decimal import Decimal
import random
from typing import List

from .models import SavingsGoal, WeeklyAllocation
from .money import quantize_amount


def monday_of_week(target_date: date) -> date:
    return target_date - timedelta(days=target_date.weekday())


def weeks_between(start_date: date, target_date: date) -> List[date]:
    current = monday_of_week(start_date)
    weeks = []
    while current <= target_date:
        weeks.append(current)
        current += timedelta(days=7)
    return weeks


def _generate_plan(
    rng: random.Random,
    total: Decimal,
    week_starts: List[date],
) -> List[Decimal]:
    attempts = 0
    max_share = Decimal("0.35")
    total_weeks = len(week_starts)
    total_cents = int((total * 100).to_integral_value())

    while attempts < 500:
        attempts += 1
        weights = [rng.random() ** 2 for _ in week_starts]
        weight_sum = sum(weights)
        raw = [total * Decimal(weight / weight_sum) for weight in weights]
        amounts = [quantize_amount(value) for value in raw]
        current_total = sum(amounts, Decimal("0.00"))
        remainder = total - current_total
        remainder_cents = int((remainder * 100).to_integral_value())
        index = 0
        step = 1 if remainder_cents >= 0 else -1
        remainder_cents = abs(remainder_cents)
        while remainder_cents > 0:
            amounts[index] = quantize_amount(
                amounts[index] + Decimal(step) * Decimal("0.01")
            )
            remainder_cents -= 1
            index = (index + 1) % len(amounts)
        max_allowed = total * max_share if total_weeks > 2 else total
        if any(amount > max_allowed for amount in amounts):
            continue
        if total >= Decimal("200"):
            preferred = sum(
                1 for amount in amounts if Decimal("5") <= amount <= Decimal("50")
            )
            if preferred < max(1, total_weeks // 2):
                continue
        if sum(amounts, Decimal("0.00")) * 100 != Decimal(total_cents) * 1:
            continue
        return amounts
    base = (total / Decimal(total_weeks)).quantize(Decimal("0.01"))
    amounts = [base for _ in range(total_weeks)]
    current_total = sum(amounts, Decimal("0.00"))
    remainder = total - current_total
    remainder_cents = int((remainder * 100).to_integral_value())
    index = 0
    while remainder_cents > 0:
        amounts[index] = quantize_amount(amounts[index] + Decimal("0.01"))
        remainder_cents -= 1
        index = (index + 1) % len(amounts)
    return amounts


def generate_weekly_plan(goal: SavingsGoal) -> SavingsGoal:
    week_starts = weeks_between(goal.start_date, goal.target_date)
    rng = random.Random(goal.seed)
    amounts = _generate_plan(rng, goal.target_price, week_starts)
    weekly_plan = [
        WeeklyAllocation(week_start=week_start, amount=amount)
        for week_start, amount in zip(week_starts, amounts)
    ]
    return replace(goal, weekly_plan=weekly_plan)
