from sqlalchemy.orm import Session
from app.services.mitigation_learning import (
    evaluate_mitigation_effectiveness,
)

def tune_mitigation_strategy(db: Session, tenant_id: str):

    effectiveness = evaluate_mitigation_effectiveness(db, tenant_id)
    learning = effectiveness["learning"]
    delta = effectiveness.get("delta", 0.0)
    adjustment = 0

    if learning == "failure":
        adjustment = 1

    elif learning == "mild_success":
        adjustment = 0

    elif learning == "strong_success":
        adjustment = -1

    return {
        "tenant_id": tenant_id,
        "learning": learning,
        "delta": delta,
        "adjustment": adjustment,
    }
