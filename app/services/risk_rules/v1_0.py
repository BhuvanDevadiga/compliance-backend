from app.services.risk_rules.base import RiskRuleset


class RiskRulesV1(RiskRuleset):
    version = "v1.0"

    def calculate(self, payload: dict):
        risk_score = 0
        reasons = []

        company_size = payload.get("company_size")
        industry = payload.get("industry", "").lower()
        has_gst = payload.get("has_gst")
        has_pan = payload.get("has_pan")

        if company_size is not None and company_size < 10:
            risk_score += 30
            reasons.append("Small company")

        if industry in ["finance", "insurance"]:
            risk_score += 40
            reasons.append("High-risk industry")

        if not has_gst:
            risk_score += 20
            reasons.append("GST not registered")

        if not has_pan:
            risk_score += 10
            reasons.append("PAN not registered")

        if risk_score >= 70:
            risk_level = "HIGH"
        elif risk_score >= 40:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return risk_score, risk_level, reasons
