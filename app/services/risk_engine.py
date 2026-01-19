from app.services.risk_rules.base import RiskDecision, RULESETS

def calculate_risk(payload: dict, version: str):
    ruleset = RULESETS[version]

    # TRACE-enabled ruleset (v1.2+)
    if hasattr(ruleset, "evaluate_with_trace"):
        return ruleset.evaluate_with_trace(payload)

    # Legacy rulesets (v1.0, v1.1)
    score, level, reasons = ruleset.evaluate(payload)
    return score, level, reasons
