from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List


class Category(str, Enum):
    FOOD = "Food"
    CLOTHING = "Clothing"
    GAS = "Gas"
    DRINKS = "Drinks"
    SPORTS = "Sports"
    GROCERY = "Grocery"
    EVENT = "Event"
    UBER = "Uber"
    RANDOM = "Random"
    INVESTING = "Investing"
    SUBSCRIPTIONS = "Subscriptions"
    SAVINGS = "Savings"


@dataclass
class Expense:
    id: str
    date: date
    category: Category
    amount: Decimal
    note: Optional[str] = None


@dataclass
class WeeklyAllocation:
    week_start: date
    amount: Decimal


@dataclass
class SavingsGoal:
    id: str
    name: str
    url: str
    target_price: Decimal
    start_date: date
    target_date: date
    seed: int
    weekly_plan: List[WeeklyAllocation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MonthData:
    monthly_income: Decimal = Decimal("0.00")
    discretionary_income: Decimal = Decimal("0.00")
    expenses: List[Expense] = field(default_factory=list)
    savings_goals: List[SavingsGoal] = field(default_factory=list)
