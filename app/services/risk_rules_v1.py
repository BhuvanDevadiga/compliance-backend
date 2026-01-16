def calculate_risk_v1(payload: dict):
    score = 0
    reasons = []

    if payload["company_size"] < 50:
        score += 20
        reasons.append("Small company")

    if payload["industry"].lower() in ["finance", "construction", "mining"]:
        score += 30
        reasons.append("High-risk industry")

    if not payload["has_gst"]:
        score += 20
        reasons.append("GST not registered")

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons,
        "ruleset_version": "v1.0"
    }
