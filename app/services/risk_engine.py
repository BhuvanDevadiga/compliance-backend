def calculate_risk_score(payload):
    score = 0
    reasons = []

    # Company size
    if payload.company_size < 10:
        score += 30
        reasons.append("Very small company")
    elif payload.company_size < 50:
        score += 20
        reasons.append("Small company")
    else:
        score += 10
        reasons.append("Medium/Large company")

    # Industry risk
    high_risk_industries = {"finance", "healthcare", "crypto"}
    if payload.industry.lower() in high_risk_industries:
        score += 30
        reasons.append(f"High-risk industry: {payload.industry}")
    else:
        score += 10
        reasons.append("Low-risk industry")

    # Compliance docs
    if not payload.has_gst:
        score += 20
        reasons.append("GST not registered")
    if not payload.has_pan:
        score += 20
        reasons.append("PAN missing")

    score = min(score, 100)

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level, reasons
