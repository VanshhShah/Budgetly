import argparse
import os
import csv
from datetime import date
import sys
import json

DATA_FILE = "expenses.csv"
FIELDNAMES = ["amount", "category", "description", "date"]
BUDGET_FILE = "budgets.json"

def parse_amount(value):
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"stop playing buddy,'{value}' is not a number")

    if amount <= 0:
        raise ValueError(f"are you in a debt bro? like who enters a negative number in expenses")

    return round(amount, 2)

def load_expenses(filepath=DATA_FILE):
    expenses = []
    if not os.path.exists(filepath):
        return expenses

    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["amount"] = float(row["amount"])
            expenses.append(row)
    return expenses

def save_expense(expense, filepath=DATA_FILE):
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(expense)

def add_expense(amount, category, description, expense_date=None, filepath=DATA_FILE):
    expense = {
        "amount": parse_amount(amount),
        "category": category.strip().lower(),
        "description": description.strip(),
        "date": expense_date or date.today().isoformat()
    }
    save_expense(expense, filepath)
    return expense

def monthly_summary(expenses, month=None):
    summary = {}
    for expense in expenses:
        if month and not expense["date"].startswith(month):
            continue
        category = expense["category"]
        summary[category] = summary.get(category, 0) + float(expense["amount"])

    result = {}
    for k, v in summary.items():
        result[k] = round(v, 2)
    return result

def load_budgets(filepath=BUDGET_FILE):
    if not os.path.exists(filepath):
        return {}
    with open(filepath) as f:
        contents = f.read().strip()
        if not contents:
            return {}
        return json.loads(contents)


def save_budgets(budgets, filepath=BUDGET_FILE):
    with open(filepath, "w")as f:
        json.dump(budgets, f, indent=2)

def set_budget(category, amount, filepath=BUDGET_FILE):
    validated_amount = parse_amount(amount)
    budgets = load_budgets(filepath)
    budgets[category.strip().lower()] = validated_amount
    save_budgets(budgets, filepath)
    return budgets


def check_budget_status(spent, budget):
    if budget <= 0:
        raise ValueError("Budget must be greater than zero")

    ratio = spent / budget
    if ratio > 1:
        return "under_budget"
    elif ratio >= 0.8:
        return "warning"
    else:
        return "over_budget"


def print_budget_status(month=None):
    expenses = load_expenses()
    budgets = load_budgets()
    summary = monthly_summary(expenses, month)

    if not budgets:
        print("No budgets set. Use 'budget-set <category> <amount>' to add one.")
        return

    icons = {"under_budget": "oh buddy! you need a sugarDaddy or sugarMommy", 
        "warning": "well well well, you are about to burn all money of your family", 
        "over_budget": "you know how to live your life in budget bud"}
    for category, budget in budgets.items():
        spent = summary.get(category, 0)
        status = check_budget_status(spent, budget)
        print(f"{category} spent ₹{spent:} / ₹{budget:.2f}  [{icons[status]}]")


def remove_expense(expenses, index):
    # used to remove any expense from the spendings
    index = int(index)

    if index < 1 or index > len(expenses):
        raise ValueError("No expense at index {index}. Valid range: 1-{len(expenses)}")
    else:
        expenses.pop(index-1)

    return expenses

def save_all_expenses(expenses, filepath=DATA_FILE):
    # saves all of your expenses in expenses.csv at last
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for expense in expenses:
            writer.writerow(expense)

def build_parser():
    parser = argparse.ArgumentParser(description="expense and budget tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_p = subparsers.add_parser("add", help="Add a new expense")
    add_p.add_argument("amount", help="expense amount")
    add_p.add_argument("category", help="expense category, ex. groceries")
    add_p.add_argument("description", help="ex. milk and bread")
    add_p.add_argument("--date", help="YYYY-MM-DD format")

    summary_p = subparsers.add_parser("summary", help="shows summary by category")
    summary_p.add_argument("--month", help="filters by month in YYYY-MM format")

    list_p = subparsers.add_parser("list", help="List expenses")        
    list_p.add_argument("--category", help="Filter by category")

    budget_set_p = subparsers.add_parser("budget-set", help="Set a monthly budget for a category")
    budget_set_p.add_argument("category")
    budget_set_p.add_argument("amount")

    subparsers.add_parser("budget-status", help="Compare spending against budgets")
    
    remove_p = subparsers.add_parser("remove", help="Remove the expense from list")
    remove_p.add_argument("index", type=int)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "add":
            expense = add_expense(args.amount, args.category, args.description, args.date)
            print(f"Added: ₹{expense[\"amount\"]:.2f} | {expense["category"]} | {expense["description"]} | {expense["date"]}")

        elif args.command == "summary":
            expenses = load_expenses()
            summary = monthly_summary(expenses, args.month)
            if not summary:
                print("No expenses found.")
            else:
                for category, amount in summary.items():
                    print(f"{category} ₹{amount}")

        elif args.command == "list":
            expenses = load_expenses()
            if args.category:
                expenses = [e for e in expenses if e["category"] == args.category.lower()]
            if not expenses:
                print("No expenses found.")
            for i, e in enumerate(expenses, start=1):
                print(f"{i}. ₹{e['amount']:.2f} | {e['category']} | {e['description']} | {e['date']}")

        elif args.command == "budget-set":
            set_budget(args.category, args.amount)
            print(f"Budget set: {args.category.lower()} -> ₹{parse_amount(args.amount):.2f}/month")

        elif args.command == "remove":
            expenses = load_expenses()
            expenses = remove_expense(expenses, args.index)
            save_all_expenses(expenses)
            print(f"removed expense: {args.index} ")

        elif args.command == "budget-status":
            print_budget_status()

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
