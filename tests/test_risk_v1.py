from app.services.risk_rules.registry import calculate_risk


def test_finance_small_company():
    payload = {
        "company_size": 5,
        "industry": "finance",
        "has_gst": False,
        "has_pan": False
    }

    score, level, reasons = calculate_risk(payload, version="v1.0")

    assert score >= 70
    assert level == "HIGH"
