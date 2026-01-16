from app.services.risk_rules_v1 import calculate_risk_v1

def calculate_risk(payload: dict, version: str = "v1.0"):
    if version == "v1.0":
        return calculate_risk_v1(payload)

    raise ValueError(f"Unsupported ruleset version: {version}")
