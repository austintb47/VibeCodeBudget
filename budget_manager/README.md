# Budget Manager (CLI)

A simple, local Python CLI budget manager. Data is stored in `data/budget.json` and is kept stable with a schema version.

## How to run

```bash
cd budget_manager
python -m src.main
```

> Requires Python 3.11+ (stdlib only).

## Example usage flow

1. Launch the app.
2. Select **Create new month**, enter `2026-02`.
3. Go to **Income & discretionary settings** and set monthly income and discretionary income.
4. Add a few expenses under **Expenses**.
5. View **Category breakdown report** for totals and remaining.
6. Add a savings goal, then generate a weekly plan.
7. Export a report to a plain text file (saved under `data/`).

## Rounding strategy (exact cents)

- **All money uses `Decimal`** (never float).
- Amounts are **quantized to 2 decimal places** at input and output boundaries.
- Daily discretionary schedules and weekly savings plans **always sum exactly** to their total by distributing leftover cents across the earliest entries.

## Weekly plan generation strategy

- Week boundaries **start on Monday**. The plan includes the Monday of the week containing the start date, then each Monday until the target date (inclusive).
- A deterministic randomized plan is generated using a stored seed.
- The generator:
  - Favors smaller weekly amounts using squared random weights.
  - Enforces **no week > 35%** of target price unless there are 2 or fewer weeks.
  - When targets are large (>= $200), it tries to keep at least half of weeks between **$5–$50**.
  - Always **sums exactly** to the target price (cents preserved).

## Sample `budget.json` snippet

```json
{
  "schema_version": 1,
  "months": {
    "2026-02": {
      "monthly_income": "4200.00",
      "discretionary_income": "800.00",
      "expenses": [
        {
          "id": "b3a7b2f5-74c8-43fe-b5d5-4c7c2e7604c5",
          "date": "2026-02-03",
          "category": "Food",
          "amount": "12.50",
          "note": "Lunch"
        }
      ],
      "savings_goals": [
        {
          "id": "7a4b4d49-6b0a-4d7a-9c8e-2f5a8e21e1c9",
          "name": "New Headphones",
          "url": "https://example.com/item",
          "target_price": "150.00",
          "start_date": "2026-02-01",
          "target_date": "2026-02-28",
          "seed": 12345,
          "weekly_plan": [
            {
              "week_start": "2026-01-26",
              "amount": "20.00"
            }
          ],
          "created_at": "2026-02-01T12:00:00"
        }
      ]
    }
  }
}
```

## Manual test cases

1. **Create month & persistence**: Create `2026-03`, quit, re-open, and verify the month still exists in the menu.
2. **Month isolation**: Add an expense in `2026-03`, switch to `2026-04`, and confirm the expense does not appear.
3. **Income weekly math**: Set income to `4000`, confirm the weekly estimates show `1000.00` and `920.60` (rounded).
4. **Discretionary schedule sum**: Set discretionary to `100.00` for February (28 days) and verify the total scheduled equals exactly `100.00`.
5. **Discretionary rounding**: Set discretionary to `100.01`, verify that the earliest days are incremented by one cent and the total remains exact.
6. **Expense validation**: Try adding a negative amount (e.g., `-5`) and confirm it is rejected.
7. **Date validation**: In month `2026-02`, attempt to add an expense on `2026-03-01`; it should be rejected.
8. **Category totals**: Add two Food expenses (`10.00`, `5.00`) and confirm Food total is `15.00`.
9. **Remaining calculation**: Set income `200`, add expenses totaling `50`, confirm Remaining is `150.00`.
10. **Savings plan sum**: Create a goal at `125.55` and generate a plan; verify weekly plan amounts sum to exactly `125.55`.
11. **Top expenses**: Add multiple expenses and confirm the top-N list shows the highest amounts first.
12. **Export report**: Use export and ensure a `report-YYYY-MM-*.txt` file appears under `data/`.
