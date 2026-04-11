from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.ml.control_risk_scorer import compute_control_failure_probability
from app.models.control import Control


def get_controls_for_tenant(db: Session, tenant_id: str):
    return (
        db.query(Control)
        .filter(Control.tenant_id == tenant_id)
        .order_by(Control.id.asc())
        .all()
    )


def classify_control_risk_level(probability: float) -> str:
    if probability >= 0.85:
        return "CRITICAL"
    if probability >= 0.65:
        return "HIGH"
    if probability >= 0.4:
        return "MEDIUM"
    return "LOW"


def score_all_controls(db: Session, tenant_id: str):
    controls = get_controls_for_tenant(db, tenant_id)
    now = datetime.now(UTC).replace(tzinfo=None)

    results = []

    for control in controls:
        prob = compute_control_failure_probability(control)
        risk_level = classify_control_risk_level(prob)

        control.control_failure_prob = prob
        control.control_risk_level = risk_level
        control.control_risk_updated_at = now

        results.append(
            {
                "control_id": control.id,
                "failure_probability": prob,
                "risk_level": risk_level,
                "updated_at": now,
            }
        )

    if controls:
        # Commit is handled at a higher level.
        db.flush()

    return results


def compute_audit_readiness(db: Session, tenant_id: str):
    controls = (
        db.query(Control)
        .filter(Control.tenant_id == tenant_id)
        .all()
    )

    if not controls:
        return 0.0

    avg_risk = sum(c.control_failure_prob for c in controls) / len(controls)

    readiness = round(1 - avg_risk, 4)

    return readiness
