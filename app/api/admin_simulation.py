from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.adaptive_risk_engine import escalate_risk
from app.services.risk_decay import decay_risk

router = APIRouter(
    prefix="/api/admin/simulate",
    tags=["Admin Simulation"],
)


@router.post("/{tenant_id}")
def simulate(
    tenant_id: str,
    mode: str = Query("stress"),
    db: Session = Depends(get_db),
):

    if mode == "escalate":
        escalate_risk(db, tenant_id, "manual_escalation", 5)

    elif mode == "stress":
        escalate_risk(db, tenant_id, "stress_test", 25)

    elif mode == "recover":
        decay_risk(db)

    else:
        return {"status": "unknown mode"}

    return {
        "tenant": tenant_id,
        "mode": mode,
        "status": "simulation executed",
    }
