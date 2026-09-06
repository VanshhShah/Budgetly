# Budgetly

#### Video Demo: https://youtu.be/KuK_YGJZoUA

#### Description:

Budgetly is a command-line expense tracker and budget monitor built in Python
as my CS50x final project. It lets a user log everyday expenses, review them
by category or by month, remove an expense they logged by mistake, set a
monthly budget for each spending category, and instantly see whether they
are under, close to, or over that budget. The goal was to build something I
would genuinely use myself: a lightweight, no-frills alternative to
spreadsheet-based budgeting that lives entirely in the terminal and stores
its data in plain CSV and JSON files, so it is easy to inspect, back up, or
import into other tools.

The project is organized around `project.py`, which contains all of the
program's logic, and `test_project.py`, which contains a suite of unit tests
written with `pytest` covering the most important pure functions. A
`requirements.txt` file lists the only external dependency (`pytest`, needed
to run the tests; the program itself uses only the Python standard library).

## How it works

Expenses are stored one per row in `expenses.csv`, with columns for date,
amount, category, and description. Budgets are stored separately in
`budgets.json`, mapping each category name to a monthly budget amount. Both
files are created automatically the first time they are needed, so a brand
new user can start typing commands immediately without any setup step.

The program is driven entirely through `argparse` subcommands:

- `add <amount> <category> <description> [--date YYYY-MM-DD]` validates and
  appends a new expense. If no date is given, today's date is used.
- `list [--category X]` prints every stored expense with a 1-based row
  number in front of it, optionally filtered down to a single category.
- `remove <index>` deletes the expense at the given row number (the same
  number shown by `list`).
- `summary [--month YYYY-MM]` groups expenses by category and prints an
  ASCII bar chart of totals, so spending patterns are visible at a glance
  without needing a graphing library.
- `budget-set <category> <amount>` creates or updates the monthly budget
  for a category (running it again for the same category simply overwrites
  the old amount).
- `budget-status` compares the current month's spending in each budgeted
  category against its budget and labels it OK, WARNING, or OVER BUDGET.

Example session:

```
$ python project.py add 45.20 groceries "Weekly shop"
Added: 2026-09-03 | ₹45.20 | groceries | Weekly shop

$ python project.py list
1. 2026-09-03 | ₹45.20 | groceries | Weekly shop

$ python project.py remove 1
removed expense: 1

$ python project.py budget-set groceries 50
Budget set: groceries -> ₹50.00/month

$ python project.py budget-status
groceries    spent ₹   0.00 / ₹50.00  [OK]
```

## Design decisions

A few functions were deliberately written as **pure functions** — taking
plain data in and returning plain data out, with no file I/O or printing
inside them — so that they could be unit tested in isolation:

- `parse_amount(value)` validates that a user-supplied amount is a real,
  positive number, and rounds it to two decimal places. This centralizes
  input validation so that both the `add` and `budget-set` commands reject
  bad input the same way, rather than duplicating checks in two places.
- `monthly_summary(expenses, month=None)` takes a list of expense
  dictionaries and returns a dictionary of category totals, optionally
  filtered to a single month. Keeping this separate from `load_expenses()`
  meant I could test the grouping and filtering logic directly against
  hand-built lists of expenses, without needing to touch the filesystem or
  create temporary CSV files for every test case.
- `check_budget_status(spent, budget)` encapsulates the threshold logic
  (under 80% is "under", 80–100% is "warning", over 100% is "over") as a
  single, easily testable decision.
- `remove_expense(expenses, index)` takes the in-memory list of expenses and
  a 1-based row number, and returns the list with that item removed. I
  chose 1-based indexing on purpose, even though Python lists are 0-based
  internally, because `list` displays expenses starting at row 1 — the
  number the user types into `remove` should match exactly what they see
  on screen, so I convert from 1-based to 0-based only at the point where
  the item is actually popped (`expenses.pop(index - 1)`). If the index is
  out of range, the function raises a `ValueError` rather than letting
  Python's own `IndexError` escape, so it gets caught by the same
  `try/except` block in `main()` that already handles every other bad-input
  case, instead of needing special-case handling just for this command.

Separating these pure functions from the I/O-heavy functions
(`load_expenses`, `save_expense`, `save_all_expenses`, `load_budgets`,
`save_budgets`, and the various `print_*` functions) made the test suite in
`test_project.py` much simpler to write, since tests could pass in plain
Python lists and dictionaries instead of setting up and tearing down real
files.

One trade-off I debated with `remove` specifically: CSV files don't support
deleting a single row in place, so removing an expense means rewriting the
_entire_ file rather than editing one line. I considered instead marking a
row as "deleted" with a flag column and filtering it out on read, which
would avoid rewriting the whole file — but that would complicate every
other function that reads `expenses.csv`, since they'd all need to remember
to skip flagged rows. Given how small this dataset realistically gets (a
personal expense log, not a production database), I decided the simplicity
of `save_all_expenses()` fully rewriting the file on every removal was the
right trade-off: one small, obvious function (`load → modify in memory →
overwrite`) instead of spreading "is this row still valid?" logic across
several places.

Error handling is centralized in `main()`: every command runs inside a
`try/except ValueError` block, so invalid input (a non-numeric amount, a
zero budget, an out-of-range row number for `remove`, and so on) is caught
in one place and reported to the user with a clear message and a non-zero
exit code, rather than crashing with a raw traceback.

## What I learned building this

This project pulled together most of what CS50 covers: functions and
control flow, file I/O (CSV and JSON), command-line argument parsing,
exception handling, and writing automated tests. The hardest part was
resisting the urge to add more features (recurring expenses, multi-currency
support, a proper charting library) and instead keeping the scope tight
enough to finish and thoroughly test in a weekend. Adding `remove` after
the initial version also taught me something about maintaining an existing
codebase: I had to trace through several existing functions (`load_expenses`,
`save_expense`) to figure out the right pattern to reuse for
`save_all_expenses`, rather than just bolting on something disconnected
from the rest of the program.

## Possible future improvements

- A `remove-budget` command to delete a previously set budget for a
  category (currently budgets can be created or updated, but not removed).
- Support editing an existing expense in place, rather than only adding or
  removing.
- Export a summary report to CSV or PDF.
- Add a `--currency` option for users tracking spending in multiple
  currencies.
- Wrap the same core logic (`parse_amount`, `monthly_summary`,
  `check_budget_status`, `remove_expense`) in a small Flask web interface.

## Files

- `project.py` — main program: all commands, validation, and I/O logic.
- `test_project.py` — pytest test suite for `parse_amount`,
  `monthly_summary`, `check_budget_status`, and `remove_expense`.
- `requirements.txt` — Python dependencies (`pytest`).
- `expenses.csv` — expenses are saved here
- `budgets.json` — budget-set is saved here
