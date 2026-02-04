from __future__ import annotations

from decimal import Decimal
from typing import Iterable, Dict, List

from .models import Expense, Category, SavingsGoal
from .money import decimal_to_str


def format_currency(amount: Decimal) -> str:
    return f"${decimal_to_str(amount)}"


def category_report_lines(
    totals: Dict[Category, Decimal],
    percentages: Dict[Category, Decimal],
) -> List[str]:
    lines = [f"{'Category':<15} | {'Total':>10} | % of spent"]
    lines.append("-" * 40)
    for category in Category:
        total = totals.get(category, Decimal("0.00"))
        percent = percentages.get(category, Decimal("0.00"))
        lines.append(
            f"{category.value:<15} | {format_currency(total):>10} | {percent:>7.2f}%"
        )
    return lines


def expenses_table(expenses: Iterable[Expense]) -> List[str]:
    lines = [f"{'ID':<8} | {'Date':<10} | {'Category':<13} | {'Amount':>10} | Note"]
    lines.append("-" * 70)
    for expense in expenses:
        short_id = expense.id.split("-")[0]
        note = expense.note or ""
        lines.append(
            f"{short_id:<8} | {expense.date.isoformat():<10} | {expense.category.value:<13} | {format_currency(expense.amount):>10} | {note}"
        )
    return lines


def top_expenses_table(expenses: Iterable[Expense]) -> List[str]:
    lines = [f"{'Rank':<4} | {'Date':<10} | {'Category':<13} | {'Amount':>10} | Note"]
    lines.append("-" * 70)
    for index, expense in enumerate(expenses, start=1):
        note = expense.note or ""
        lines.append(
            f"{index:<4} | {expense.date.isoformat():<10} | {expense.category.value:<13} | {format_currency(expense.amount):>10} | {note}"
        )
    return lines


def goals_table(goals: Iterable[SavingsGoal]) -> List[str]:
    lines = [f"{'ID':<8} | {'Name':<20} | {'Target':>10} | {'Target Date':<10}"]
    lines.append("-" * 60)
    for goal in goals:
        short_id = goal.id.split("-")[0]
        lines.append(
            f"{short_id:<8} | {goal.name[:20]:<20} | {format_currency(goal.target_price):>10} | {goal.target_date.isoformat():<10}"
        )
    return lines


def weekly_plan_table(goal: SavingsGoal) -> List[str]:
    lines = [f"{'Week Start':<12} | {'Amount':>10}"]
    lines.append("-" * 30)
    for allocation in goal.weekly_plan:
        lines.append(
            f"{allocation.week_start.isoformat():<12} | {format_currency(allocation.amount):>10}"
        )
    return lines
