from sqlalchemy.orm import Session
from app.models.risk_assessment import RiskAssessment


def get_risk_history(
    db: Session,
    tenant_id: str,
    limit: int = 10,
):
    return (
        db.query(RiskAssessment)
        .filter(RiskAssessment.tenant_id == tenant_id)
        .order_by(RiskAssessment.created_at.desc())
        .limit(limit)
        .all()
    )
