from sqlalchemy.orm import Session
from app.models.behavior_memory import BehaviorMemory

SEVERITY_WEIGHTS = {
    "stable behavior": 1,
    "elevated behavior": 2,   
    "critical behavior": 4,
}

def compute_tenant_behavior_score(db: Session, tenant_id: str, window: int = 25) :
    """
    Compute a behavior score for the tenant based on recent history.

    Uses a weighted average of recent behavior classifications,
    with more weight on critical behaviors.
    """

    history = (
        db.query(BehaviorMemory)
        .filter(BehaviorMemory.tenant_id == tenant_id)
        .order_by(BehaviorMemory.timestamp.desc())
        .limit(window)
        .all()
    )

    if not history:
        return {
            "score": 0.0, "risk_level": "unknown", "window": 0,
        }

    

    weighted_score = sum(
        SEVERITY_WEIGHTS.get(h.classification, 1) 
          for h in history
    )
    score = weighted_score / (len(history))

    if score < 1.8:
        level = "stable tenant"
    elif score < 3:
        level = "elevated tenant"
    else:
        level = "high-risk tenant"

    return {
        "score": round(score, 2),
        "risk_level": level,
        "window": len(history),
    }

