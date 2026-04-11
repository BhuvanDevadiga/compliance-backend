from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.db.session import get_db
from app.services.adaptive_risk_engine import escalate_risk, deescalate_risk
from app.services.risk_simulator import SimulationInput, simulate_risk

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class SimulationRequest(BaseModel):
    base_risk: int
    escalation_events: int
    mitigation_strength: int


@router.post("/simulate")
def simulate(req: SimulationRequest):

    input_data = SimulationInput(
        base_risk=req.base_risk,
        escalation_events=req.escalation_events,
        mitigation_strength=req.mitigation_strength,
    )

    return simulate_risk(input_data)

@router.post("/simulate/{tenant_id}")
def simulate_tenant(tenant_id: str, mode: str, db=Depends(get_db)):

    if mode == "stress":
        with db.begin():
            escalate_risk(db, tenant_id, "stress_test", 25)

    elif mode == "recover":
        with db.begin():
            deescalate_risk(db, tenant_id, "recovery_test", 20)

    return {
        "tenant": tenant_id,
        "mode": mode,
        "status": "simulation executed",
    }

