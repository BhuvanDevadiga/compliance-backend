from typing import List, Tuple
from app.services.risk_rules.base import RiskRuleset, RuleHit, RiskDecision


class RiskRulesV12(RiskRuleset):
    version = "v1.2"
    status = "active"
    introduced_on = "2026-01-15"
    description = "Risk scoring with rule-hit audit trail"

    @classmethod
    def evaluate_with_trace(cls, payload: dict) -> RiskDecision:
        score = 0
        reasons: List[str] = []
        hits: List[RuleHit] = []

        # ---- Rule: Company Size ----
        company_size = payload.get("company_size", 0)
        if company_size < 10:
            score += 20
            reasons.append("Very small company")
            hits.append(RuleHit(rule="SMALL_COMPANY", points=20))

        # ---- Rule: Industry Risk ----
        industry = payload.get("industry", "").lower()
        if industry in {"crypto", "finance"}:
            score += 30
            reasons.append("High-risk industry")
            hits.append(RuleHit(rule="HIGH_RISK_INDUSTRY", points=30))

        # ---- Rule: GST ----
        if not payload.get("has_gst", True):
            score += 25
            reasons.append("GST not registered")
            hits.append(RuleHit(rule="NO_GST", points=25))

        # ---- Rule: PAN ----
        if not payload.get("has_pan", True):
            score += 15
            reasons.append("PAN missing")
            hits.append(RuleHit(rule="NO_PAN", points=15))

        # ---- Risk Level ----
        if score >= 70:
            level = "high"
        elif score >= 40:
            level = "medium"
        else:
            level = "low"

        return RiskDecision(
            score=score,
            level=level,
            reasons=reasons,
            rules_fired=hits
        )