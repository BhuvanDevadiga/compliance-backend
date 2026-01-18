from app.services.risk_rules.registry import calculate_risk

def test_crypto_company_high_risk():
    payload = {
        "company_size": 8,
        "industry": "crypto",
        "has_gst": False,
        "has_pan": False
    }

    score, level, reasons = calculate_risk(payload, version="v1.2")

    assert score >= 100
    assert level == "HIGH"
    assert "crypto" in " ".join(reasons).lower()
