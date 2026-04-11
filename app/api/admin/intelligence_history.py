from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.risk_intelligence_snapshot import RiskIntelligenceSnapshot

router = APIRouter(prefix="/api/admin/intelligence", tags=["Admin Intelligence"])


@router.get("/{tenant_id}")
def get_history(tenant_id: str, db: Session = Depends(get_db)):

    history = (
        db.query(RiskIntelligenceSnapshot)
        .filter_by(tenant_id=tenant_id)
        .order_by(RiskIntelligenceSnapshot.timestamp.desc())
        .limit(50)
        .all()
    )

    return history
