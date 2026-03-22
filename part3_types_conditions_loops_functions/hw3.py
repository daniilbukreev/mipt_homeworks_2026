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


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    return year % 4 == 0 and year % 100 != 0 or year % 400 == 0


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    words = list(maybe_dt.split())
    date = ""
    for i in words:
        if i.count("-") == 2:
            date = i
            break
    date_parts = list(date.split("-"))
    day = date_parts[0]
    month = date_parts[1]
    year = date_parts[2]
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    if len(year) != 4 or int(year) == 1984:
        print(INCORRECT_DATE_MSG)
        return None
    if year[0] == "0":
        print(INCORRECT_DATE_MSG)
        return None
    for i in year:
        if i not in numbers:
            print(INCORRECT_DATE_MSG)
            return None

    if month not in ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]:
        print(INCORRECT_DATE_MSG)
        return None

    if len(day) != 2:
        print(INCORRECT_DATE_MSG)
        return None
    if day[0] not in numbers or day[1] not in numbers:
        print(INCORRECT_DATE_MSG)
        return None
    if day == "00":
        print(INCORRECT_DATE_MSG)
        return None

    if month in ["01", "03", "05", "07", "08", "10", "12"]:
        if int(day) > 31:
            print(INCORRECT_DATE_MSG)
            return None
    elif month == "02":
        if is_leap_year(int(year)):
            if int(day) > 29:
                print(INCORRECT_DATE_MSG)
                return None
        else:
            if int(day) > 28:
                print(INCORRECT_DATE_MSG)
                return None
    else:
        if int(day) > 30:
            print(INCORRECT_DATE_MSG)
            return None

    return (int(day), int(month), int(year))

def extract_amount(amount: str) -> float | None:
    for i in amount:
        if i not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ",", ".", "-"]:
            print(UNKNOWN_COMMAND_MSG)
            return None

    if amount[0] == "0":
        print(UNKNOWN_COMMAND_MSG)
        return None
    if amount[0] == "," or amount[0] == ".":
        print(UNKNOWN_COMMAND_MSG)
        return None
    if amount[-1] == "," or amount[-1] == ".":
        print(UNKNOWN_COMMAND_MSG)
        return None


    dots = amount.count(",") + amount.count(".")
    if dots > 1:
        print(UNKNOWN_COMMAND_MSG)
        return None
    if dots == 1:
        amount = amount.replace("," , ".")
    if amount[0] == "-":
        print(UNKNOWN_COMMAND_MSG)
        return None

    return float(amount)

def income_handler(amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"amount": amount, "date": income_date})
    return OP_SUCCESS_MSG

def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    financial_transactions_storage.append({"category": category_name, "amount": amount, "date": income_date})
    return OP_SUCCESS_MSG

def cost_categories_handler() -> str:
    return "\n".join(f"{k}: {v}" for k, v in EXPENSE_CATEGORIES.items())

def stats_handler(report_date: str) -> str:
    inc_month = 0
    out_month = 0

    inc_uptodate = 0
    out_uptodate = 0

    category_outcomes = dict()
    for i in financial_transactions_storage:
        if len(i) == 2:
            if i["date"] <= report_date:
                inc_uptodate += i["amount"]
            if i["date"][1] == report_date[1] and i["date"][2] == report_date[2]:
                inc_month += i["amount"]
        if len(i) == 3:
            if i["date"] <= report_date:
                out_uptodate += i["amount"]
            if i["date"][1] == report_date[1] and i["date"][2] == report_date[2]:
                out_month += i["amount"]
                if (category_outcomes.get(i["category"]) == None):
                    category_outcomes[i["category"]] = 0
                category_outcomes[i["category"]] += i["amount"]

    print(f"Your statistics as of {report_date[0]:02d}-{report_date[1]:02d}-{report_date[2]:02d}:")
    print(f"Total capital: {(inc_uptodate - out_uptodate):.2f} rubles")
    res = inc_month - out_month
    if (res >= 0):
        print(f"This month, the profit amounted to {res:.2f} rubles.")
    else:
        print(f"This month, the loss amounted to {abs(res):.2f} rubles.")
    print(f"Income: {inc_month:.2f} rubles")
    print(f"Expenses: {out_month:.2f} rubles")
    print()
    print("Details (category: amount):")
    count = 1
    for key, value in category_outcomes.items():
        print(f"{count}. {key}: {value}")
        count += 1
    return ""

def line_handler(s: str) -> None:
    words = list(s.split())
    if len(words) == 3 and words[0] == "income":
        amount_number = extract_amount(words[1])
        if amount_number == None:
            return None
        date =  extract_date(words[2])
        if date == None:
            return None
        print(income_handler(amount_number, date))

    elif len(words) == 4 and words[0] == "cost":
        category_name = words[1]
        category_name_split = list(category_name.split("::"))
        common_category = category_name_split[0]
        target_category = category_name_split[1]
        if EXPENSE_CATEGORIES.get(common_category) == None:
            print(cost_categories_handler())
            print(NOT_EXISTS_CATEGORY)
        if target_category not in EXPENSE_CATEGORIES[common_category]:
            print(cost_categories_handler())
            print(NOT_EXISTS_CATEGORY)
        amount_number = extract_amount(words[2])
        if amount_number == None:
            return None
        date = extract_date(words[3])
        if date == None:
            return None
        print(cost_handler(target_category, amount_number, date))

    elif len(words) == 2:
        if words[0] == "stats":
            date = extract_date(words[1])
            if date == None:
                return None
            print(stats_handler(date), end = "")
        if words[0] == "cost":
            if words[1] == "categories":
                print(cost_categories_handler())
                return None
    else:
        print(UNKNOWN_COMMAND_MSG)

def main() -> None:
    while True:
        s = input()
        if not s:
            break
        line_handler(s)


if __name__ == "__main__":
    main()
