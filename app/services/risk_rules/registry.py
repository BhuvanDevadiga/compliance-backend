from app.services.risk_rules.v1_0 import RiskRulesV1

RULESETS = {
    "v1.0": RiskRulesV1,
}

def calculate_risk(payload: dict, version: str = "v1.0"):
    ruleset_cls = RULESETS.get(version)

    if not ruleset_cls:
        raise ValueError(f"Unknown ruleset version: {version}")

    ruleset = ruleset_cls()    
    return ruleset.calculate(payload)
