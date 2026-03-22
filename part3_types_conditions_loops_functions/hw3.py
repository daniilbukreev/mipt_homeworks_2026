#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}

DATE_PARTS_LEN = 3
YEAR_LEN = 4
MONTH_LEN = 2
DAY_LEN = 2
MONTHS_IN_YEAR = 12
MAX_DAYS_IN_MONTH = 31
FEBRUARY = 2
INCOME_COMMAND_LEN = 3
COST_CATEGORIES_COMMAND_LEN = 2
COST_COMMAND_LEN = 4
CATEGORY_PARTS_LEN = 2
STATS_COMMAND_LEN = 2
KEY_AMOUNT = "amount"
KEY_DATE = "date"
KEY_CATEGORY = "category"

type DateComparable = tuple[int, int, int]
type MonthlyStats = tuple[float, float, dict[str, float]]

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    is_divisible_by_four = year % 4 == 0
    is_not_divisible_by_hundred = year % 100 != 0
    is_divisible_by_four_hundred = year % 400 == 0
    return (is_divisible_by_four and is_not_divisible_by_hundred) or is_divisible_by_four_hundred


def _is_valid_date_parts(parts: list[str]) -> bool:
    if len(parts) != DATE_PARTS_LEN:
        return False
    return all(part.isdigit() for part in parts)


def _is_valid_day(day: int, month: int, year: int) -> bool:
    days_in_month = MAX_DAYS_IN_MONTH
    if month in {4, 6, 9, 11}:
        days_in_month = 30
    elif month == FEBRUARY:
        days_in_month = 29 if is_leap_year(year) else 28
    return 1 <= day <= days_in_month


def extract_date(maybe_dt: str) -> DateComparable | None:
    parts = maybe_dt.split("-")
    if not _is_valid_date_parts(parts):
        return None

    day, month, year = map(int, parts)

    if not (
        (len(parts[2]) == YEAR_LEN and year > 0) and
        (len(parts[1]) == MONTH_LEN and 1 <= month <= MONTHS_IN_YEAR) and
        (len(parts[0]) == DAY_LEN and _is_valid_day(day, month, year))
    ):
        return None

    return day, month, year


def extract_amount(amount_str: str) -> float | None:
    if amount_str.count(",") + amount_str.count(".") > 1:
        return None
    amount_number = amount_str.replace(",", ".")
    if not amount_number.replace(".", "", 1).lstrip("-").isdigit():
        return None
    if amount_number[0] == "." or amount_number[-1] == ".":
        return None

    return float(amount_number)


def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({KEY_AMOUNT: amount, KEY_DATE: income_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append({KEY_CATEGORY: category_name, KEY_AMOUNT: amount, KEY_DATE: income_date})
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(f"{k}: {v}" for k, v in EXPENSE_CATEGORIES.items())


def date_gentle(date_str: str) -> DateComparable:
    parts = date_str.split("-")
    year = int(parts[2])
    month = int(parts[1])
    day = int(parts[0])
    return year, month, day


def get_monthly_stats(report_date_comparable: DateComparable) -> MonthlyStats:
    monthly_income = 0
    monthly_expense = 0
    category_expenses: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if date_gentle(transaction[KEY_DATE])[:2] == report_date_comparable[:2]:
            category = transaction.get(KEY_CATEGORY)
            if category is None:
                monthly_income += transaction[KEY_AMOUNT]
            else:
                monthly_expense += transaction[KEY_AMOUNT]
                category_expenses[category] = category_expenses.get(category, 0) + transaction[KEY_AMOUNT]
    return monthly_income, monthly_expense, category_expenses


def get_total_capital(report_date_comparable: DateComparable) -> float:
    uptill_income = 0
    uptill_expense = 0

    for i in financial_transactions_storage:
        date = date_gentle(i[KEY_DATE])
        if date <= report_date_comparable:
            if KEY_CATEGORY in i:
                uptill_expense += i[KEY_AMOUNT]
            else:
                uptill_income += i[KEY_AMOUNT]
    return uptill_income - uptill_expense


def _print_monthly_profit_loss(month_income: float, month_expense: float) -> None:
    month_res = month_income - month_expense
    if month_res >= 0:
        print(f"This month, the profit amounted to {month_res:.2f} rubles.")
    else:
        print(f"This month, the loss amounted to {abs(month_res):.2f} rubles.")


def _print_category_expenses(category_expenses: dict[str, float]) -> None:
    print()
    print("Details (category: amount):")
    if category_expenses:
        for j, (category, amount) in enumerate(sorted(category_expenses.items()), 1):
            print(f"{j}. {category}: {amount:.2f}")


def _print_statistics_report(report_date: str, report_date_comparable: DateComparable) -> None:
    month_income, month_expense, category_expenses = get_monthly_stats(report_date_comparable)
    uptill_capital = get_total_capital(report_date_comparable)

    print(f"Your statistics as of {report_date}:")
    print(f"Total capital: {uptill_capital:.2f} rubles")
    _print_monthly_profit_loss(month_income, month_expense)
    print(f"Income: {month_income:.2f} rubles")
    print(f"Expenses: {month_expense:.2f} rubles")
    _print_category_expenses(category_expenses)


def stats_handler(report_date: str) -> None:
    report_date_comparable = date_gentle(report_date)
    _print_statistics_report(report_date, report_date_comparable)


def income(words: list[str]) -> None:
    if len(words) != INCOME_COMMAND_LEN:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount_str, date_str = words[1], words[2]
    amount = extract_amount(amount_str)

    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
    elif amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
    elif extract_date(date_str) is None:
        print(INCORRECT_DATE_MSG)
    else:
        print(income_handler(amount, date_str))


def _validate_cost_command_structure(words: list[str]) -> str | None:
    if len(words) == COST_COMMAND_LEN:
        return None
    return UNKNOWN_COMMAND_MSG


def _parse_and_validate_category(category_str: str) -> str | None:
    category_parts = category_str.split("::")
    if len(category_parts) != CATEGORY_PARTS_LEN:
        return NOT_EXISTS_CATEGORY

    common_category, target_category = category_parts
    if common_category not in EXPENSE_CATEGORIES:
        return NOT_EXISTS_CATEGORY
    if target_category not in EXPENSE_CATEGORIES.get(common_category, []):
        return NOT_EXISTS_CATEGORY
    return None


def _validate_amount_and_date(amount_str: str, date_str: str) -> tuple[float | None, str | None]:
    amount = extract_amount(amount_str)
    if amount is None:
        return None, UNKNOWN_COMMAND_MSG
    if amount <= 0:
        return None, NONPOSITIVE_VALUE_MSG
    if extract_date(date_str) is None:
        return None, INCORRECT_DATE_MSG
    return amount, None


def _validate_cost_input(words: list[str]) -> str | None:
    error_message = _validate_cost_command_structure(words)
    if error_message:
        return error_message

    error_message = _parse_and_validate_category(words[1])
    if error_message:
        return error_message

    amount, error_message = _validate_amount_and_date(words[2], words[3])
    if error_message:
        return error_message

    _, target_category = words[1].split("::")
    return cost_handler(target_category, amount, words[3])


def cost(words: list[str]) -> None:
    if len(words) == COST_CATEGORIES_COMMAND_LEN and words[1] == "categories":
        print(cost_categories_handler())
        return

    error_message = _validate_cost_input(words)
    if error_message:
        print(error_message)
        if error_message == NOT_EXISTS_CATEGORY:
            print(cost_categories_handler())


def stats(words: list[str]) -> None:
    if len(words) != STATS_COMMAND_LEN:
        print(UNKNOWN_COMMAND_MSG)
        return
    date_str = words[1]
    if extract_date(date_str) is None:
        print(INCORRECT_DATE_MSG)
        return
    stats_handler(date_str)


def line_handler(line: str) -> None:
    words = line.split()
    if not words:
        print(UNKNOWN_COMMAND_MSG)
        return

    command = words[0]
    if command == "income":
        income(words)
    elif command == "cost":
        cost(words)
    elif command == "stats":
        stats(words)
    else:
        print(UNKNOWN_COMMAND_MSG)


def main() -> None:
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line:
            break
        line_handler(line)


if __name__ == "__main__":
    main()
