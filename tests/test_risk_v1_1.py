from app.services.risk_rules.registry import calculate_risk

def test_v1_1_crypto_high_risk():
    payload = {
        "company_size": 5,
        "industry": "crypto",
        "has_gst": False,
        "has_pan": False
    }

    score, level, reasons = calculate_risk(payload, version="v1.1")

    assert score >= 80
    assert level == "HIGH"
    assert "High-risk industry: crypto" in reasons
