import json
from pathlib import Path
from app.services.risk_rules.base import RiskRuleset

CONFIG_PATH = Path(__file__).parent / "configs" / "v1_1.json"


class RiskRulesV1_1(RiskRuleset):
    version = "v1.1"

    def __init__(self):
        with open(CONFIG_PATH) as f:
            self.config = json.load(f)

    def calculate(self, payload: dict):
        risk_score = 0
        reasons = []

        # Company size
        size_cfg = self.config["company_size"]["small"]
        if payload["company_size"] < size_cfg["max"]:
            risk_score += size_cfg["score"]
            reasons.append("Small company")

        # Industry
        industry = payload["industry"].lower()
        if industry in self.config["industry"]:
            risk_score += self.config["industry"][industry]
            reasons.append(f"High-risk industry: {industry}")

        # Documents
        if not payload["has_gst"]:
            risk_score += self.config["documents"]["gst_missing"]
            reasons.append("GST not registered")

        if not payload["has_pan"]:
            risk_score += self.config["documents"]["pan_missing"]
            reasons.append("PAN not registered")

        # Risk level
        if risk_score >= self.config["thresholds"]["HIGH"]:
            level = "HIGH"
        elif risk_score >= self.config["thresholds"]["MEDIUM"]:
            level = "MEDIUM"
        else:
            level = "LOW"

        return risk_score, level, reasons
