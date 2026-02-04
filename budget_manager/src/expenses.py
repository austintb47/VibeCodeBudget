from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Dict, Optional, Iterable

from .models import Expense, Category
from .money import quantize_amount


def add_expense(
    expenses: List[Expense],
    expense_date: date,
    category: Category,
    amount: Decimal,
    note: Optional[str],
    expense_id: str,
) -> Expense:
    expense = Expense(
        id=expense_id,
        date=expense_date,
        category=category,
        amount=quantize_amount(amount),
        note=note,
    )
    expenses.append(expense)
    return expense


def list_expenses(
    expenses: Iterable[Expense],
    category: Optional[Category] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[Expense]:
    filtered = []
    for expense in expenses:
        if category and expense.category != category:
            continue
        if start_date and expense.date < start_date:
            continue
        if end_date and expense.date > end_date:
            continue
        filtered.append(expense)
    return sorted(filtered, key=lambda exp: (exp.date, exp.id), reverse=True)


def total_spent(expenses: Iterable[Expense]) -> Decimal:
    return sum((expense.amount for expense in expenses), Decimal("0.00"))


def category_totals(expenses: Iterable[Expense]) -> Dict[Category, Decimal]:
    totals = {category: Decimal("0.00") for category in Category}
    for expense in expenses:
        totals[expense.category] += expense.amount
    return {category: quantize_amount(amount) for category, amount in totals.items()}


def category_percentages(
    totals: Dict[Category, Decimal], total: Decimal
) -> Dict[Category, Decimal]:
    if total <= 0:
        return {category: Decimal("0.00") for category in totals}
    return {
        category: quantize_amount((amount / total) * Decimal("100"))
        for category, amount in totals.items()
    }


def remaining_income(monthly_income: Decimal, spent: Decimal) -> Decimal:
    return quantize_amount(monthly_income - spent)


def find_expense(expenses: Iterable[Expense], expense_id: str) -> Optional[Expense]:
    for expense in expenses:
        if expense.id == expense_id:
            return expense
    return None


def top_expenses(expenses: Iterable[Expense], count: int) -> List[Expense]:
    return sorted(expenses, key=lambda exp: exp.amount, reverse=True)[:count]
