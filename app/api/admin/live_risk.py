from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.tenant_risk_state import TenantRiskState

router = APIRouter(prefix="/api/admin/live-risk", tags=["Live Risk"])


@router.get("/")
def live_risk_snapshot(db: Session = Depends(get_db)):

    states = db.query(TenantRiskState).all()

    return [
        {
            "tenant": s.tenant_id,
            "score": s.risk_score,
            "level": s.risk_level,
            "quarantined": s.quarantined,
            "updated": s.updated_at,
        }
        for s in states
    ]
