from sqlalchemy.orm import Session
from app.models.risk import RiskAssessment

def get_risk_history(
    db: Session,
    company_id: int,
    regulation: str,
    limit: int = 10
):
    return (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.company_id == company_id,
            RiskAssessment.regulation == regulation
        )
        .order_by(RiskAssessment.created_at.desc())
        .limit(limit)
        .all()
    )
