from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any

from .money import decimal_to_str, str_to_decimal
from .models import MonthData, Expense, SavingsGoal, WeeklyAllocation, Category

SCHEMA_VERSION = 1
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_FILE = DATA_DIR / "budget.json"


def ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_data({"schema_version": SCHEMA_VERSION, "months": {}})


def load_data() -> Dict[str, Any]:
    ensure_storage()
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_data(data: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def month_from_dict(data: Dict[str, Any]) -> MonthData:
    expenses = [
        Expense(
            id=item["id"],
            date=date.fromisoformat(item["date"]),
            category=Category(item["category"]),
            amount=str_to_decimal(item["amount"]),
            note=item.get("note"),
        )
        for item in data.get("expenses", [])
    ]
    goals = [
        SavingsGoal(
            id=item["id"],
            name=item["name"],
            url=item["url"],
            target_price=str_to_decimal(item["target_price"]),
            start_date=date.fromisoformat(item["start_date"]),
            target_date=date.fromisoformat(item["target_date"]),
            seed=item["seed"],
            weekly_plan=[
                WeeklyAllocation(
                    week_start=date.fromisoformat(plan["week_start"]),
                    amount=str_to_decimal(plan["amount"]),
                )
                for plan in item.get("weekly_plan", [])
            ],
            created_at=datetime.fromisoformat(item["created_at"]),
        )
        for item in data.get("savings_goals", [])
    ]
    return MonthData(
        monthly_income=str_to_decimal(data.get("monthly_income", "0.00")),
        discretionary_income=str_to_decimal(data.get("discretionary_income", "0.00")),
        expenses=expenses,
        savings_goals=goals,
    )


def month_to_dict(month: MonthData) -> Dict[str, Any]:
    return {
        "monthly_income": decimal_to_str(month.monthly_income),
        "discretionary_income": decimal_to_str(month.discretionary_income),
        "expenses": [
            {
                "id": expense.id,
                "date": expense.date.isoformat(),
                "category": expense.category.value,
                "amount": decimal_to_str(expense.amount),
                "note": expense.note,
            }
            for expense in month.expenses
        ],
        "savings_goals": [
            {
                "id": goal.id,
                "name": goal.name,
                "url": goal.url,
                "target_price": decimal_to_str(goal.target_price),
                "start_date": goal.start_date.isoformat(),
                "target_date": goal.target_date.isoformat(),
                "seed": goal.seed,
                "weekly_plan": [
                    {
                        "week_start": allocation.week_start.isoformat(),
                        "amount": decimal_to_str(allocation.amount),
                    }
                    for allocation in goal.weekly_plan
                ],
                "created_at": goal.created_at.isoformat(),
            }
            for goal in month.savings_goals
        ],
    }


def load_months() -> Dict[str, MonthData]:
    data = load_data()
    months = {
        key: month_from_dict(value) for key, value in data.get("months", {}).items()
    }
    return months


def save_months(months: Dict[str, MonthData]) -> None:
    data = {
        "schema_version": SCHEMA_VERSION,
        "months": {key: month_to_dict(value) for key, value in months.items()},
    }
    save_data(data)
