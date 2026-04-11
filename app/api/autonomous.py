from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_tenant
from app.services import autonomous_analytics
from typing import List
from app.schemas.autonomous import DecisionResponse
from app.services.system_state import compute_system_state
from app.schemas.autonomous import SystemStateResponse

router = APIRouter(
    prefix="/api/autonomous",
    tags=["Autonomous Intelligence"],
)
@router.get("/decisions", response_model=List[DecisionResponse])
def get_decision_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant),
):
    decisions = autonomous_analytics.get_decisions(
        db, tenant.tenant_id, limit
    )
    return decisions

    
@router.get("/forecast-accuracy")
def forecast_accuracy(
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant),
):
    return autonomous_analytics.get_forecast_accuracy(
        db, tenant.tenant_id
    )
@router.get("/strategy-performance")
def strategy_performance(
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant),
):
    return autonomous_analytics.get_strategy_performance(
        db, tenant.tenant_id
    )

@router.get("/system-state", response_model=SystemStateResponse)
def get_system_state(
    db: Session = Depends(get_db),
    tenant = Depends(get_current_tenant),
):
    return compute_system_state(db, tenant.tenant_id)