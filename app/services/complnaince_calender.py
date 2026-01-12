from datetime import date
from dateutil.relativedelta import relativedelta
import json
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent.parent

def load_india_rules():
    rules_path = BASE_PATH / "compliance_rules" / "india"
    rules = {}

    for file in rules_path.glob("*.json"):
        with open(file) as f:
            rules[file.stem] = json.load(f)

    return rules


RULES = load_india_rules()



def next_month_due(due_day: int):
    today = date.today()
    next_month = today + relativedelta(months=1)
    return date(next_month.year, next_month.month, due_day)


def annual_due(due_month: int, due_day: int):
    today = date.today()
    year = today.year
    due_date = date(year, due_month, due_day)

    if due_date < today:
        due_date = date(year + 1, due_month, due_day)

    return due_date


def quarterly_due(due_month: int, due_day: int):
    today = date.today()
    year = today.year
    due_date = date(year, due_month, due_day)

    if due_date < today:
        due_date = date(year + 1, due_month, due_day)

    return due_date



def get_applicable_compliances(user: dict):
    applicable = []

    applicability = RULES["applicability"]

    if user.get("gst_registered"):
        applicable.append(RULES["gst"])

    if user.get("has_employees_or_contractors"):
        applicable.append(RULES["tds"])

    return applicable


def generate_compliance_calendar(user: dict):
    calendar = []
    compliances = get_applicable_compliances(user)

    for compliance in compliances:
        for item in compliance["returns"]:
            frequency = item["frequency"]

            if frequency == "monthly":
                due_date = next_month_due(item["due_day"])

            elif frequency == "quarterly":
                due_date = quarterly_due(
                    item["due_month"],
                    item["due_day"]
                )

            elif frequency == "annual":
                due_date = annual_due(
                    item["due_month"],
                    item["due_day"]
                )

            else:
                continue

            calendar.append({
                "code": item["code"],
                "name": item["name"],
                "type": compliance["type"],
                "due_date": due_date.isoformat(),
                "frequency": frequency,
                "penalty": item.get("penalty", {})
            })

    return sorted(calendar, key=lambda x: x["due_date"])
