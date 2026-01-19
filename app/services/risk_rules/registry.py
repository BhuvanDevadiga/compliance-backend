from app.services.risk_rules.v1_0 import RiskRulesV10
from app.services.risk_rules.v1_1 import RiskRulesV11
from app.services.risk_rules.v1_2 import RiskRulesV12

RULESETS = {
    "v1.0": RiskRulesV10,
    "v1.1": RiskRulesV11,
    "v1.2": RiskRulesV12,
}

def calculate_risk(
    payload: dict,
    version: str = "v1.2",
    allow_frozen: bool = False,
):
    ruleset_cls = RULESETS.get(version)

    if not ruleset_cls:
        raise ValueError(f"Unknown ruleset version: {version}")

    status = getattr(ruleset_cls, "status", "active")

    if status == "deprecated":
        raise ValueError(f"Ruleset {version} is deprecated")

    if status == "frozen" and not allow_frozen:
        raise ValueError(f"Ruleset {version} is frozen")

    ruleset = ruleset_cls()
    return ruleset.calculate(payload)

def list_rule_versions():
    return [
        ruleset.metadata()
        for ruleset in RULESETS.values()
    ]


def get_rule_metadata(version: str):
    ruleset = RULESETS.get(version)

    if not ruleset:
        raise ValueError(f"Unknown ruleset version: {version}")

    return ruleset.metadata()