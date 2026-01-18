from app.services.risk_rules.v1_0 import RiskRulesV1
from app.services.risk_rules.v1_1 import RiskRulesV1_1
from app.services.risk_rules.v1_2 import RiskRulesV1_2

RULESETS = {
    "v1.0": RiskRulesV1,
    "v1.1": RiskRulesV1_1,
    "v1.2": RiskRulesV1_2
}

def calculate_risk(payload: dict, version: str = "v1.0"):
    ruleset_cls = RULESETS.get(version)

    if not ruleset_cls:
        raise ValueError(f"Unknown ruleset version: {version}")

    ruleset = ruleset_cls()
    return ruleset.calculate(payload)

