#!/usr/bin/env python3
"""
Expense Tracker CLI - Track, summarize, and manage personal expenses.
Includes AI category prediction, insight, and Indian Rupee currency.
"""

import argparse
import json
import os
import sys
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# ------------------------------------------------------------
# Configuration & Data paths
# ------------------------------------------------------------
DATA_DIR = Path.home() / ".expense_tracker"
EXPENSES_FILE = DATA_DIR / "expenses.json"
BUDGETS_FILE = DATA_DIR / "budgets.json"

# ------------------------------------------------------------
# Data initialization
# ------------------------------------------------------------
def init_data_files():
    """Create data directory and default files if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    if not EXPENSES_FILE.exists():
        with open(EXPENSES_FILE, "w") as f:
            json.dump([], f)
    if not BUDGETS_FILE.exists():
        with open(BUDGETS_FILE, "w") as f:
            json.dump({}, f)

def load_expenses():
    with open(EXPENSES_FILE, "r") as f:
        return json.load(f)

def save_expenses(expenses):
    with open(EXPENSES_FILE, "w") as f:
        json.dump(expenses, f, indent=2)

def load_budgets():
    with open(BUDGETS_FILE, "r") as f:
        return json.load(f)

def save_budgets(budgets):
    with open(BUDGETS_FILE, "w") as f:
        json.dump(budgets, f, indent=2)

# ------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------
def get_next_id(expenses):
    """Return the next available ID (max id + 1)."""
    if not expenses:
        return 1
    return max(e["id"] for e in expenses) + 1

def validate_date(date_str):
    """Return datetime.date object if valid, else None."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

def parse_month(month_str):
    """Return (year, month) from 'YYYY-MM' string."""
    try:
        year, month = map(int, month_str.split("-"))
        return year, month
    except:
        return None, None

def format_currency(amount):
    """Return string like '₹12.50'."""
    return f"₹{amount:.2f}"          # Changed to Indian Rupee

def print_table(rows, headers, show_total=False, total_amount=0):
    """Simple table formatter using column widths."""
    if not rows:
        print("No data to display.")
        return
    # Compute column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    # Print header
    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        line = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(line)
    # Print total row if requested
    if show_total:
        print("-" * len(header_line))
        total_line = f"TOTAL".ljust(col_widths[0]) + " | " + format_currency(total_amount).ljust(col_widths[1])
        print(total_line)

# ------------------------------------------------------------
# AI Category Prediction
# ------------------------------------------------------------
def predict_category(description):
    """Predict category based on keywords in the description."""
    desc = description.lower()

    if any(word in desc for word in ["pizza", "burger", "food", "restaurant", "dinner", "lunch", "coffee", "snack", "meal"]):
        return "Food"
    elif any(word in desc for word in ["bus", "train", "uber", "auto", "taxi", "metro", "fuel", "petrol", "diesel"]):
        return "Transport"
    elif any(word in desc for word in ["shirt", "clothes", "shopping", "mall", "amazon", "flipkart", "online"]):
        return "Shopping"
    elif any(word in desc for word in ["movie", "netflix", "game", "prime", "hotstar", "spotify", "cinema"]):
        return "Entertainment"
    elif any(word in desc for word in ["rent", "electricity", "water", "bill", "gas"]):
        return "Utilities"
    else:
        return "Other"

# ------------------------------------------------------------
# Command implementations
# ------------------------------------------------------------
def cmd_add(args):
    expenses = load_expenses()
    # Date handling
    if args.date:
        date_obj = validate_date(args.date)
        if not date_obj:
            print(f"Invalid date format: {args.date}. Use YYYY-MM-DD.")
            return
        date_str = args.date
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_obj = datetime.now().date()

    # Amount validation
    try:
        amount = float(args.amount)
        if amount <= 0:
            print("Amount must be positive.")
            return
    except ValueError:
        print("Invalid amount. Use a number (e.g., 12.50).")
        return

    # Category logic: use provided or predict from description
    if args.category:
        category = args.category
    else:
        category = predict_category(args.description)
        print(f"🤖 Predicted Category: {category}")

    new_expense = {
        "id": get_next_id(expenses),
        "date": date_str,
        "amount": amount,
        "category": category,
        "description": args.description or "",
    }
    expenses.append(new_expense)
    save_expenses(expenses)
    print(f"Expense added (ID: {new_expense['id']})")

    # Budget check for this category and month
    budgets = load_budgets()
    if category in budgets:
        limit = budgets[category]
        # Sum expenses for same category in same month
        total = sum(
            e["amount"] for e in expenses
            if e["category"] == category
            and e["date"].startswith(date_str[:7])  # same YYYY-MM
        )
        if total > limit:
            print(f"⚠️  Budget alert: {category} exceeded {format_currency(limit)} limit (total: {format_currency(total)})")
        elif total > limit * 0.9:
            print(f"⚠️  Budget warning: {category} at {total/limit*100:.0f}% of {format_currency(limit)} limit")

def cmd_list(args):
    expenses = load_expenses()
    filtered = expenses[:]

    # Filter by category
    if args.category:
        filtered = [e for e in filtered if e["category"].lower() == args.category.lower()]

    # Filter by date range
    if args.from_date:
        start = validate_date(args.from_date)
        if start:
            filtered = [e for e in filtered if validate_date(e["date"]) >= start]
        else:
            print(f"Invalid --from date: {args.from_date}. Ignoring filter.")
    if args.to_date:
        end = validate_date(args.to_date)
        if end:
            filtered = [e for e in filtered if validate_date(e["date"]) <= end]
        else:
            print(f"Invalid --to date: {args.to_date}. Ignoring filter.")

    if not filtered:
        print("No expenses match the criteria.")
        return

    # Prepare rows for table
    rows = [
        [e["id"], e["date"], format_currency(e["amount"]), e["category"], e["description"]]
        for e in sorted(filtered, key=lambda x: x["date"])
    ]
    total_amount = sum(e["amount"] for e in filtered)
    print_table(rows, ["ID", "Date", "Amount", "Category", "Description"], show_total=True, total_amount=total_amount)

def cmd_summary(args):
    expenses = load_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    # Filter by month if provided
    if args.month:
        year, month = parse_month(args.month)
        if year is None:
            print("Invalid month format. Use YYYY-MM (e.g., 2025-03).")
            return
        month_expenses = [
            e for e in expenses
            if e["date"].startswith(f"{year}-{month:02d}")
        ]
        title = f"Summary for {year}-{month:02d}"
    else:
        month_expenses = expenses
        title = "Overall Summary"

    if not month_expenses:
        print(f"No expenses in {args.month if args.month else 'records'}.")
        return

    total = sum(e["amount"] for e in month_expenses)
    # Group by category
    cat_totals = defaultdict(float)
    for e in month_expenses:
        cat_totals[e["category"]] += e["amount"]

    # AI Insight: top category
    if cat_totals:
        top_category = max(cat_totals, key=cat_totals.get)
        print(f"\n🤖 Insight: You spend most on {top_category}. Consider reducing it.")

    # Prepare table rows
    rows = []
    for cat, amt in sorted(cat_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (amt / total) * 100 if total else 0
        rows.append([cat, format_currency(amt), f"{percentage:.1f}%"])

    print(f"\n{title}")
    print_table(rows, ["Category", "Amount", "% of Total"])
    # Print total separately for emphasis
    print(f"\n💰 TOTAL AMOUNT: {format_currency(total)}")
    print(f"📊 Number of transactions: {len(month_expenses)}")

def cmd_total(args):
    """Show total expenses for a specific month or overall."""
    expenses = load_expenses()
    if not expenses:
        print("No expenses recorded yet.")
        return

    if args.month:
        year, month = parse_month(args.month)
        if year is None:
            print("Invalid month format. Use YYYY-MM (e.g., 2025-03).")
            return
        month_expenses = [
            e for e in expenses
            if e["date"].startswith(f"{year}-{month:02d}")
        ]
        if not month_expenses:
            print(f"No expenses found for {args.month}.")
            return
        total = sum(e["amount"] for e in month_expenses)
        print(f"💰 Total expenses for {args.month}: {format_currency(total)}")
        print(f"📊 Transactions: {len(month_expenses)}")
    else:
        total = sum(e["amount"] for e in expenses)
        print(f"💰 Total expenses (all time): {format_currency(total)}")
        print(f"📊 Total transactions: {len(expenses)}")

def cmd_delete(args):
    expenses = load_expenses()
    found = None
    for i, e in enumerate(expenses):
        if e["id"] == args.id:
            found = i
            break
    if found is None:
        print(f"No expense with ID {args.id}.")
        return
    removed = expenses.pop(found)
    save_expenses(expenses)
    print(f"Deleted expense ID {args.id}: {removed['date']} {removed['category']} {format_currency(removed['amount'])}")

def cmd_export(args):
    expenses = load_expenses()
    if not expenses:
        print("Nothing to export.")
        return

    if args.format == "json":
        out_file = "expenses_export.json"
        with open(out_file, "w") as f:
            json.dump(expenses, f, indent=2)
        print(f"Exported {len(expenses)} expenses to {out_file}")
    elif args.format == "csv":
        out_file = "expenses_export.csv"
        with open(out_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "date", "amount", "category", "description"])
            writer.writeheader()
            writer.writerows(expenses)
        print(f"Exported {len(expenses)} expenses to {out_file}")
    else:
        print("Unsupported format. Use 'json' or 'csv'.")

def cmd_budget(args):
    budgets = load_budgets()
    if args.set:
        category = args.set
        # Check that limit is provided
        if args.limit is None:
            print("Please provide --limit with --set")
            return
        limit = args.limit
        if limit <= 0:
            print("Limit must be positive.")
            return
        budgets[category] = limit
        save_budgets(budgets)
        print(f"Budget for '{category}' set to {format_currency(limit)}")
    elif args.show:
        # Show budgets with current spending for the current month
        current_month = datetime.now().strftime("%Y-%m")
        expenses = load_expenses()
        month_expenses = [e for e in expenses if e["date"].startswith(current_month)]
        cat_spending = defaultdict(float)
        for e in month_expenses:
            cat_spending[e["category"]] += e["amount"]

        if not budgets:
            print("No budgets defined.")
            return

        rows = []
        for cat, limit in sorted(budgets.items()):
            spent = cat_spending.get(cat, 0)
            remaining = limit - spent
            status = "OK" if remaining >= 0 else "OVER"
            rows.append([cat, format_currency(limit), format_currency(spent), format_currency(remaining), status])
        print_table(rows, ["Category", "Limit", "Spent (this month)", "Remaining", "Status"])
    else:
        # No subcommand - print usage
        print("Usage: expense_tracker.py budget --set <category> --limit <amount>")
        print("       expense_tracker.py budget --show")

# ------------------------------------------------------------
# Main argument parser
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Expense Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # add
    parser_add = subparsers.add_parser("add", help="Add a new expense")
    parser_add.add_argument("--amount", required=True, help="Amount (e.g., 12.50)")
    parser_add.add_argument("--category", help="Category (optional, AI will predict if not given)")
    parser_add.add_argument("--description", default="", help="Description (used for AI prediction)")
    parser_add.add_argument("--date", help="Date YYYY-MM-DD (default: today)")

    # list
    parser_list = subparsers.add_parser("list", help="List expenses")
    parser_list.add_argument("--category", help="Filter by category")
    parser_list.add_argument("--from", dest="from_date", help="Start date YYYY-MM-DD")
    parser_list.add_argument("--to", dest="to_date", help="End date YYYY-MM-DD")

    # summary
    parser_summary = subparsers.add_parser("summary", help="Show spending summary")
    parser_summary.add_argument("--month", help="Month in YYYY-MM format (default: all time)")

    # total
    parser_total = subparsers.add_parser("total", help="Show total expenses for a month or overall")
    parser_total.add_argument("--month", help="Month in YYYY-MM format (optional, shows overall if omitted)")

    # delete
    parser_delete = subparsers.add_parser("delete", help="Delete an expense by ID")
    parser_delete.add_argument("--id", required=True, type=int, help="Expense ID")

    # export
    parser_export = subparsers.add_parser("export", help="Export expenses to file")
    parser_export.add_argument("--format", choices=["json", "csv"], default="json", help="Export format")

    # budget
    parser_budget = subparsers.add_parser("budget", help="Manage budgets")
    budget_group = parser_budget.add_mutually_exclusive_group(required=True)
    budget_group.add_argument("--set", metavar="CATEGORY", help="Set budget for a category")
    budget_group.add_argument("--show", action="store_true", help="Show all budgets with current spending")
    parser_budget.add_argument("--limit", type=float, help="Budget limit (required with --set)")

    args = parser.parse_args()

    # Ensure data files exist
    init_data_files()

    # Dispatch
    if args.command == "add":
        cmd_add(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "summary":
        cmd_summary(args)
    elif args.command == "total":
        cmd_total(args)
    elif args.command == "delete":
        cmd_delete(args)
    elif args.command == "export":
        cmd_export(args)
    elif args.command == "budget":
        cmd_budget(args)

if __name__ == "__main__":
    main()
