from sqlalchemy.orm import Session
from app.services.tenant_intelligence_service import get_tenant_intelligence
from app.services.timeline_service import get_tenant_timeline

def compute_tenant_risk(db: Session, tenant_id: str):

    intelligence = get_tenant_intelligence(db, tenant_id)

    health = intelligence["health_index"]
    governance = intelligence["governance_score"]
    drift = intelligence["latest_drift"]
    bandit_conf = intelligence["bandit_confidence"]

    
    health_risk = 1 - health
    governance_risk = 1 - governance
    drift_risk = min(drift * 2, 1)

    
    risk_score = (
        0.4 * health_risk +
        0.3 * governance_risk +
        0.2 * drift_risk +
        0.1 * (1 - bandit_conf)
    )

    risk_score = round(risk_score, 4)

    if risk_score < 0.3:
        posture = "low_risk"
    elif risk_score < 0.6:
        posture = "moderate_risk"
    else:
        posture = "high_risk"

    return {
        "tenant_id": tenant_id,
        "tenant_risk_score": risk_score,
        "risk_posture": posture,
        "components": {
            "health_risk": round(health_risk, 4),
            "governance_risk": round(governance_risk, 4),
            "drift_risk": round(drift_risk, 4),
            "bandit_uncertainty": round(1 - bandit_conf, 4)
        }
    }