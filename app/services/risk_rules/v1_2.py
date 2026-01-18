from app.services.risk_rules.base import RiskRuleset
from app.services.risk_rules.loader import load_rules

class RiskRulesV1_2(RiskRuleset):
    version = "v1.2"

    def __init__(self):
        self.rules = load_rules("v1.2")

    def calculate(self, payload: dict):
        score = 0
        reasons = []

        company_size = payload.get("company_size")
        industry = payload.get("industry", "").lower()

        # Company size rule
        if company_size is not None and company_size < 10:
            score += self.rules["company_size"]["lt_10"]
            reasons.append("Small company")

        # Industry rule
        industry_risk = self.rules["industry"].get(industry)
        if industry_risk:
            score += industry_risk
            reasons.append(f"High-risk industry: {industry}")

        # Compliance rules
        if not payload.get("has_gst"):
            score += self.rules["compliance"]["missing_gst"]
            reasons.append("GST not registered")

        if not payload.get("has_pan"):
            score += self.rules["compliance"]["missing_pan"]
            reasons.append("PAN not registered")

        # Risk level
        thresholds = self.rules["thresholds"]

        if score >= thresholds["high"]:
            level = "HIGH"
        elif score >= thresholds["medium"]:
            level = "MEDIUM"
        else:
            level = "LOW"

        return score, level, reasons
