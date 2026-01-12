import json
from pathlib import Path

BASE_PATH = Path(__file__).resolve().parent.parent

def load_rules():
    rules = {}
    rules_path = BASE_PATH / "compliance_rules" / "india"

    for file in rules_path.glob("*.json"):
        with open(file) as f:
            rules[file.stem] = json.load(f)

    return rules

COMPLIANCE_RULES = load_rules()
def get_compliance_rule(country_code: str, rule_name: str):
    country_rules = COMPLIANCE_RULES.get(country_code)
    if country_rules:
        return country_rules.get(rule_name)
    return None