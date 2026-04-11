from sqlalchemy.orm import Session
from app.models.mitigation_outcome import MitigationOutcome
from app.models.behavior_memory import BehaviorMemory

def evaluate_mitigation_effectiveness(
    db: Session,
    tenant_id: str,
    window: int = 5,
):
    
    history = (
        db.query(BehaviorMemory)
        .filter(BehaviorMemory.tenant_id == tenant_id)
        .order_by(BehaviorMemory.timestamp.desc())
        .limit(window+1)
        .all()
    )

    if len(history) < window + 1:
        return {
            "learning": "insufficient_data",
            "adjustment": "none",
        }
    before = history[-1].behavior_score
    after_avg = sum(float(h.behavior_score or 0.0) for h in history[:-1]) / window
    improvement = before - after_avg

    if improvement > 0.2:
        signal = "strong_success"
        adjustment = -1

    elif improvement > 0:
        signal = "mild_success"
        adjustment = 0

    else:
        signal = "failure"
        adjustment = 1

    return {
        "learning": signal,
        "adjustment": adjustment,
        "delta": improvement,
    }