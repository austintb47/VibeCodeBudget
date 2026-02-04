from __future__ import annotations

import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional
import uuid

from .calculations import (
    weekly_income_simple,
    weekly_income_average,
    daily_discretionary_schedule,
    daily_schedule_with_dates,
    days_in_month,
)
from .expenses import (
    add_expense,
    list_expenses,
    total_spent,
    category_totals,
    category_percentages,
    remaining_income,
    find_expense,
    top_expenses,
)
from .goals import generate_weekly_plan
from .models import MonthData, Category, SavingsGoal
from .money import parse_amount, decimal_to_str, quantize_amount
from .reports import (
    category_report_lines,
    expenses_table,
    top_expenses_table,
    goals_table,
    weekly_plan_table,
    format_currency,
)
from .storage import load_months, save_months

EXPORT_DIR = Path(__file__).resolve().parents[1] / "data"


class BudgetCLI:
    def __init__(self) -> None:
        self.months = load_months()
        self.current_month: Optional[str] = None

    def run(self) -> None:
        while True:
            self.print_header()
            print("1) Select month (YYYY-MM)")
            print("2) Create new month")
            print("3) View month dashboard")
            print("4) Income & discretionary settings")
            print("5) Expenses (add/view/edit/delete)")
            print("6) Category breakdown report")
            print("7) Savings goals (add/generate/view)")
            print("8) Export reports (plain text)")
            print("9) Quit")
            choice = input("Choose an option: ").strip()
            if choice == "1":
                self.select_month()
            elif choice == "2":
                self.create_month()
            elif choice == "3":
                self.view_dashboard()
            elif choice == "4":
                self.income_settings()
            elif choice == "5":
                self.expense_menu()
            elif choice == "6":
                self.category_report()
            elif choice == "7":
                self.savings_menu()
            elif choice == "8":
                self.export_reports()
            elif choice == "9":
                print("Goodbye!")
                return
            else:
                print("Invalid choice. Please try again.")

    def print_header(self) -> None:
        print("\n=== Budget Manager ===")
        if self.current_month:
            print(f"Current month: {self.current_month}")
        else:
            print("No month selected.")

    def select_month(self) -> None:
        month = input("Enter month (YYYY-MM): ").strip()
        if not self.validate_month(month):
            print("Invalid month format. Use YYYY-MM.")
            return
        if month not in self.months:
            create = input("Month not found. Create it? (y/n): ").strip().lower()
            if create != "y":
                return
            self.months[month] = MonthData()
            save_months(self.months)
        self.current_month = month
        print(f"Selected month {month}.")

    def create_month(self) -> None:
        month = input("Enter new month (YYYY-MM): ").strip()
        if not self.validate_month(month):
            print("Invalid month format. Use YYYY-MM.")
            return
        if month in self.months:
            print("Month already exists.")
            return
        self.months[month] = MonthData()
        save_months(self.months)
        self.current_month = month
        print(f"Created and selected month {month}.")

    def ensure_month(self) -> Optional[MonthData]:
        if not self.current_month:
            print("Select a month first.")
            return None
        return self.months[self.current_month]

    def view_dashboard(self) -> None:
        month_data = self.ensure_month()
        if not month_data:
            return
        spent = total_spent(month_data.expenses)
        remaining = remaining_income(month_data.monthly_income, spent)
        print("\n--- Month Dashboard ---")
        print(f"Monthly income: {format_currency(month_data.monthly_income)}")
        print(f"Discretionary income: {format_currency(month_data.discretionary_income)}")
        print(f"Total spent: {format_currency(spent)}")
        print(f"Remaining: {format_currency(remaining)}")
        print(f"Expenses count: {len(month_data.expenses)}")
        print(f"Savings goals: {len(month_data.savings_goals)}")

    def income_settings(self) -> None:
        month_data = self.ensure_month()
        if not month_data:
            return
        while True:
            print("\n--- Income & Discretionary Settings ---")
            print(f"Monthly income: {format_currency(month_data.monthly_income)}")
            print(f"Discretionary income: {format_currency(month_data.discretionary_income)}")
            print("1) Set monthly income")
            print("2) View weekly income")
            print("3) Set discretionary income")
            print("4) View discretionary schedule")
            print("5) Back")
            choice = input("Choose: ").strip()
            if choice == "1":
                self.set_monthly_income(month_data)
            elif choice == "2":
                self.view_weekly_income(month_data)
            elif choice == "3":
                self.set_discretionary_income(month_data)
            elif choice == "4":
                self.view_discretionary_schedule(month_data)
            elif choice == "5":
                return
            else:
                print("Invalid choice.")

    def set_monthly_income(self, month_data: MonthData) -> None:
        raw = input("Enter monthly income: ").strip()
        try:
            amount = parse_amount(raw)
        except ValueError as exc:
            print(exc)
            return
        month_data.monthly_income = amount
        if month_data.discretionary_income > amount:
            month_data.discretionary_income = amount
        save_months(self.months)
        print("Monthly income updated.")

    def view_weekly_income(self, month_data: MonthData) -> None:
        simple = weekly_income_simple(month_data.monthly_income)
        average = weekly_income_average(month_data.monthly_income)
        print("\nWeekly income estimates:")
        print(f"Monthly / 4: {format_currency(simple)}")
        print(f"Monthly / 4.345: {format_currency(average)}")

    def set_discretionary_income(self, month_data: MonthData) -> None:
        raw = input("Enter discretionary income: ").strip()
        try:
            amount = parse_amount(raw)
        except ValueError as exc:
            print(exc)
            return
        if amount > month_data.monthly_income:
            print("Discretionary income cannot exceed monthly income.")
            return
        month_data.discretionary_income = amount
        save_months(self.months)
        print("Discretionary income updated.")

    def view_discretionary_schedule(self, month_data: MonthData) -> None:
        schedule = daily_discretionary_schedule(
            self.current_month, month_data.discretionary_income
        )
        total_days = len(schedule)
        if total_days == 0:
            print("No days available for schedule.")
            return
        total = sum(schedule, Decimal("0.00"))
        per_day = schedule[0] if schedule else Decimal("0.00")
        print("\nDiscretionary schedule summary:")
        print(f"Days in month: {total_days}")
        print(f"Typical per day: {format_currency(per_day)}")
        print(f"Total scheduled: {format_currency(total)}")
        detail = input("Show full day-by-day list? (y/n): ").strip().lower()
        if detail == "y":
            print("\nDate       | Amount")
            print("-" * 22)
            for day, amount in daily_schedule_with_dates(
                self.current_month, schedule
            ):
                print(f"{day.isoformat()} | {format_currency(amount)}")

    def expense_menu(self) -> None:
        month_data = self.ensure_month()
        if not month_data:
            return
        while True:
            print("\n--- Expenses ---")
            print("1) Add expense")
            print("2) List expenses")
            print("3) Edit expense")
            print("4) Delete expense")
            print("5) Back")
            choice = input("Choose: ").strip()
            if choice == "1":
                self.add_expense_cli(month_data)
            elif choice == "2":
                self.list_expenses_cli(month_data)
            elif choice == "3":
                self.edit_expense_cli(month_data)
            elif choice == "4":
                self.delete_expense_cli(month_data)
            elif choice == "5":
                return
            else:
                print("Invalid choice.")

    def add_expense_cli(self, month_data: MonthData) -> None:
        expense_date = self.prompt_date_in_month("Expense date (YYYY-MM-DD): ")
        if not expense_date:
            return
        category = self.prompt_category()
        if not category:
            return
        raw_amount = input("Amount: ").strip()
        try:
            amount = parse_amount(raw_amount)
        except ValueError as exc:
            print(exc)
            return
        note = input("Note (optional): ").strip() or None
        add_expense(
            month_data.expenses,
            expense_date,
            category,
            amount,
            note,
            str(uuid.uuid4()),
        )
        save_months(self.months)
        print("Expense added.")

    def list_expenses_cli(self, month_data: MonthData) -> None:
        category = None
        if input("Filter by category? (y/n): ").strip().lower() == "y":
            category = self.prompt_category()
            if not category:
                return
        start_date = None
        end_date = None
        if input("Filter by date range? (y/n): ").strip().lower() == "y":
            start_date = self.prompt_date_in_month("Start date (YYYY-MM-DD): ")
            end_date = self.prompt_date_in_month("End date (YYYY-MM-DD): ")
            if not start_date or not end_date:
                return
        items = list_expenses(month_data.expenses, category, start_date, end_date)
        if not items:
            print("No expenses found.")
            return
        for line in expenses_table(items):
            print(line)

    def edit_expense_cli(self, month_data: MonthData) -> None:
        if not month_data.expenses:
            print("No expenses to edit.")
            return
        target = self.choose_expense(month_data)
        if not target:
            return
        new_date = self.prompt_date_in_month(
            f"New date ({target.date.isoformat()}): ", allow_blank=True
        )
        if new_date:
            target.date = new_date
        new_category = self.prompt_category(
            f"New category ({target.category.value}): ", allow_blank=True
        )
        if new_category:
            target.category = new_category
        raw_amount = input(f"New amount ({decimal_to_str(target.amount)}): ").strip()
        if raw_amount:
            try:
                target.amount = parse_amount(raw_amount)
            except ValueError as exc:
                print(exc)
                return
        raw_note = input(
            f"New note ({target.note or 'none'}): ").strip()
        if raw_note:
            target.note = raw_note
        save_months(self.months)
        print("Expense updated.")

    def delete_expense_cli(self, month_data: MonthData) -> None:
        if not month_data.expenses:
            print("No expenses to delete.")
            return
        target = self.choose_expense(month_data)
        if not target:
            return
        confirm = input("Delete this expense? (y/n): ").strip().lower()
        if confirm != "y":
            print("Deletion cancelled.")
            return
        month_data.expenses = [exp for exp in month_data.expenses if exp.id != target.id]
        save_months(self.months)
        print("Expense deleted.")

    def choose_expense(self, month_data: MonthData):
        items = list_expenses(month_data.expenses)
        for index, expense in enumerate(items, start=1):
            print(
                f"{index}) {expense.date.isoformat()} {expense.category.value} {format_currency(expense.amount)}"
            )
        choice = input("Select by number or ID: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(items):
                return items[index - 1]
            print("Invalid selection.")
            return None
        expense = find_expense(month_data.expenses, choice)
        if not expense:
            print("Expense not found.")
        return expense

    def category_report(self) -> None:
        month_data = self.ensure_month()
        if not month_data:
            return
        totals = category_totals(month_data.expenses)
        spent = total_spent(month_data.expenses)
        percentages = category_percentages(totals, spent)
        print("\n--- Category Breakdown ---")
        for line in category_report_lines(totals, percentages):
            print(line)
        remaining = remaining_income(month_data.monthly_income, spent)
        print("\nTotals:")
        print(f"Total spent: {format_currency(spent)}")
        print(f"Monthly income: {format_currency(month_data.monthly_income)}")
        print(f"Remaining: {format_currency(remaining)}")
        if input("Show top expenses? (y/n): ").strip().lower() == "y":
            count_raw = input("How many top expenses?: ").strip()
            count = int(count_raw) if count_raw.isdigit() else 5
            for line in top_expenses_table(top_expenses(month_data.expenses, count)):
                print(line)

    def savings_menu(self) -> None:
        month_data = self.ensure_month()
        if not month_data:
            return
        while True:
            print("\n--- Savings Goals ---")
            print("1) Add goal")
            print("2) Generate weekly plan for goal")
            print("3) View goals")
            print("4) Back")
            choice = input("Choose: ").strip()
            if choice == "1":
                self.add_goal_cli(month_data)
            elif choice == "2":
                self.generate_goal_plan_cli(month_data)
            elif choice == "3":
                self.view_goals_cli(month_data)
            elif choice == "4":
                return
            else:
                print("Invalid choice.")

    def add_goal_cli(self, month_data: MonthData) -> None:
        name = input("Goal name: ").strip()
        if not name:
            print("Name is required.")
            return
        url = input("URL: ").strip()
        raw_target = input("Target price: ").strip()
        try:
            target_price = parse_amount(raw_target)
        except ValueError as exc:
            print(exc)
            return
        start_date = self.prompt_date_in_month(
            "Start date (YYYY-MM-DD, blank for month start): ", allow_blank=True
        )
        if not start_date:
            start_date = date.fromisoformat(f"{self.current_month}-01")
        target_date = self.prompt_date_in_month(
            "Target date (YYYY-MM-DD, blank for month end): ", allow_blank=True
        )
        if not target_date:
            last_day = days_in_month(self.current_month)
            target_date = date.fromisoformat(f"{self.current_month}-{last_day:02d}")
        seed_raw = input("Seed (optional): ").strip()
        seed = int(seed_raw) if seed_raw.isdigit() else int(uuid.uuid4().int % 100000)
        goal = SavingsGoal(
            id=str(uuid.uuid4()),
            name=name,
            url=url,
            target_price=target_price,
            start_date=start_date,
            target_date=target_date,
            seed=seed,
        )
        month_data.savings_goals.append(goal)
        save_months(self.months)
        print("Goal added.")

    def generate_goal_plan_cli(self, month_data: MonthData) -> None:
        goal = self.choose_goal(month_data)
        if not goal:
            return
        updated = generate_weekly_plan(goal)
        month_data.savings_goals = [
            updated if item.id == goal.id else item for item in month_data.savings_goals
        ]
        save_months(self.months)
        print("Weekly plan generated and saved.")

    def view_goals_cli(self, month_data: MonthData) -> None:
        if not month_data.savings_goals:
            print("No savings goals.")
            return
        for line in goals_table(month_data.savings_goals):
            print(line)
        detail = input("View a goal's weekly plan? (y/n): ").strip().lower()
        if detail != "y":
            return
        goal = self.choose_goal(month_data)
        if not goal:
            return
        if not goal.weekly_plan:
            print("Goal does not have a weekly plan yet.")
            return
        for line in weekly_plan_table(goal):
            print(line)

    def choose_goal(self, month_data: MonthData):
        for index, goal in enumerate(month_data.savings_goals, start=1):
            print(f"{index}) {goal.name} ({format_currency(goal.target_price)})")
        choice = input("Select by number or ID: ").strip()
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(month_data.savings_goals):
                return month_data.savings_goals[index - 1]
            print("Invalid selection.")
            return None
        for goal in month_data.savings_goals:
            if goal.id == choice:
                return goal
        print("Goal not found.")
        return None

    def export_reports(self) -> None:
        month_data = self.ensure_month()
        if not month_data:
            return
        export_lines = []
        export_lines.append(f"Budget Manager Report - {self.current_month}")
        export_lines.append("=")
        spent = total_spent(month_data.expenses)
        remaining = remaining_income(month_data.monthly_income, spent)
        export_lines.append(f"Monthly income: {format_currency(month_data.monthly_income)}")
        export_lines.append(
            f"Discretionary income: {format_currency(month_data.discretionary_income)}"
        )
        export_lines.append(f"Total spent: {format_currency(spent)}")
        export_lines.append(f"Remaining: {format_currency(remaining)}")
        export_lines.append("")
        totals = category_totals(month_data.expenses)
        percentages = category_percentages(totals, spent)
        export_lines.extend(category_report_lines(totals, percentages))
        export_lines.append("")
        export_lines.append("Expenses:")
        export_lines.extend(expenses_table(list_expenses(month_data.expenses)))
        export_lines.append("")
        export_lines.append("Savings goals:")
        export_lines.extend(goals_table(month_data.savings_goals))
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        export_path = EXPORT_DIR / f"report-{self.current_month}-{timestamp}.txt"
        export_path.write_text("\n".join(export_lines), encoding="utf-8")
        print(f"Report exported to {export_path}")

    def prompt_category(
        self, prompt: str = "Category: ", allow_blank: bool = False
    ) -> Optional[Category]:
        print("Available categories:")
        for category in Category:
            print(f"- {category.value}")
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        for category in Category:
            if raw.lower() == category.value.lower():
                return category
        print("Invalid category.")
        return None

    def prompt_date_in_month(
        self, prompt: str, allow_blank: bool = False
    ) -> Optional[date]:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return None
        try:
            value = date.fromisoformat(raw)
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return None
        if self.current_month and not value.isoformat().startswith(self.current_month):
            print("Date must be inside the selected month.")
            return None
        return value

    @staticmethod
    def validate_month(month: str) -> bool:
        try:
            datetime.strptime(month, "%Y-%m")
        except ValueError:
            return False
        return True


def run_cli() -> None:
    cli = BudgetCLI()
    cli.run()


