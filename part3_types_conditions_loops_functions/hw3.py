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
    "Other": (),
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

financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    is_divisible_by_4 = year % 4 == 0
    is_not_divisible_by_100 = year % 100 != 0
    is_divisible_by_400 = year % 400 == 0
    return (is_divisible_by_4 and is_not_divisible_by_100) or is_divisible_by_400


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    parts = list(maybe_dt.split("-"))
    if len(parts) == DATE_PARTS_LEN and all(part.isdigit() for part in parts):
        day, month, year = map(int, parts)
        if (
            len(parts[2]) == YEAR_LEN
            and year > 0
            and len(parts[1]) == MONTH_LEN
            and 1 <= month <= MONTHS_IN_YEAR
            and len(parts[0]) == DAY_LEN
            and 1 <= day <= MAX_DAYS_IN_MONTH
        ):
            days_in_month = MAX_DAYS_IN_MONTH
            if month in {4, 6, 9, 11}:
                days_in_month = 30
            elif month == FEBRUARY:
                days_in_month = 29 if is_leap_year(year) else 28
            if 1 <= day <= days_in_month:
                return day, month, year
    return None


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


def date_gentle(date_str: str) -> tuple[int, int, int]:
    parts = list(date_str.split("-"))
    return int(parts[2]), int(parts[1]), int(parts[0])


def get_monthly_stats(report_date_comparable: tuple[int, int, int]) -> tuple[float, float, dict[str, float]]:
    month_income = 0
    month_expense = 0
    month_category_expenses: dict[str, float] = {}

    for i in financial_transactions_storage:
        date = date_gentle(i[KEY_DATE])
        if date[0] == report_date_comparable[0] and date[1] == report_date_comparable[1]:
            if KEY_CATEGORY in i:
                month_expense += i[KEY_AMOUNT]
                category = i[KEY_CATEGORY]
                if month_category_expenses.get(category) is None:
                    month_category_expenses[category] = 0
                month_category_expenses[category] += i[KEY_AMOUNT]
            else:
                month_income += i[KEY_AMOUNT]
    return month_income, month_expense, month_category_expenses


def get_total_capital(report_date_comparable: tuple[int, int, int]) -> float:
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


def stats_handler(report_date: str) -> str:
    report_date_comparable = date_gentle(report_date)
    month_income, month_expense, month_category_expenses = get_monthly_stats(report_date_comparable)
    uptill_capital = get_total_capital(report_date_comparable)
    month_res = month_income - month_expense

    print(f"Your statistics as of {report_date}:")
    print(f"Total capital: {uptill_capital:.2f} rubles")
    if month_res >= 0:
        print(f"This month, the profit amounted to {month_res:.2f} rubles.")
    else:
        print(f"This month, the loss amounted to {abs(month_res):.2f} rubles.")
    print(f"Income: {month_income:.2f} rubles")
    print(f"Expenses: {month_expense:.2f} rubles")
    print()
    print("Details (category: amount):")

    if month_category_expenses:
        sorted_expenses = sorted(month_category_expenses.items())
        for j, (category, amount) in enumerate(sorted_expenses, 1):
            print(f"{j}. {category}: {amount:.2f}")

    return ""


def income(words: list[str]) -> None:
    if len(words) != INCOME_COMMAND_LEN:
        print(UNKNOWN_COMMAND_MSG)
        return

    amount_str = words[1]
    date_str = words[2]
    amount = extract_amount(amount_str)

    if amount is None:
        print(UNKNOWN_COMMAND_MSG)
        return
    if amount <= 0:
        print(NONPOSITIVE_VALUE_MSG)
        return
    if extract_date(date_str) is None:
        print(INCORRECT_DATE_MSG)
        return

    print(income_handler(amount, date_str))


def cost(words: list[str]) -> None:
    if len(words) == COST_CATEGORIES_COMMAND_LEN and words[1] == "categories":
        print(cost_categories_handler())
    elif len(words) == COST_COMMAND_LEN:
        category_str, amount_str, date_str = words[1], words[2], words[3]
        category_parts = list(category_str.split("::"))
        if len(category_parts) == CATEGORY_PARTS_LEN:
            common_category, target_category = category_parts
            if common_category in EXPENSE_CATEGORIES and target_category in EXPENSE_CATEGORIES[common_category]:
                amount = extract_amount(amount_str)
                if amount is not None and amount > 0 and extract_date(date_str) is not None:
                    print(cost_handler(target_category, amount, date_str))
                elif amount is None:
                    print(UNKNOWN_COMMAND_MSG)
                elif amount <= 0:
                    print(NONPOSITIVE_VALUE_MSG)
                else:
                    print(INCORRECT_DATE_MSG)
            else:
                print(NOT_EXISTS_CATEGORY)
                print(cost_categories_handler())
        else:
            print(NOT_EXISTS_CATEGORY)
            print(cost_categories_handler())
    else:
        print(UNKNOWN_COMMAND_MSG)


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
    words = list(line.split())
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
        line = input()
        if not line:
            break
        line_handler(line)


if __name__ == "__main__":
    main()
