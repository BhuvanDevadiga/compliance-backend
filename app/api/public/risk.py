from fastapi import APIRouter, Depends, Request
import os
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.db.database import get_db
from app.models.risk_assessment import RiskAssessment
from app.models.tenant_risk_state import TenantRiskState
from app.schemas.risk import RiskScoreRequest, RiskScoreResponse, RiskScoreOut
from app.services.risk_rules.registry import calculate_risk
from app.core.auth import get_current_tenant
from app.core.rate_limiter import limiter, tenant_rate_limit
from app.models.tenant import Tenant
from app.services.event_service import emit_event
from app.services.adaptive_enforcement import enforce_tenant_policy
from app.services.risk_enforcement import enforce_risk_policy
from app.core.redis_client import redis_client




COMPANY_SIZE_MAP = {
    "micro": 5,
    "small": 20,
    "medium": 100,
    "large": 500,
}


router = APIRouter(
    prefix="/api/public/risk",
    tags=["public-risk"]
)

@router.post("/score", response_model=RiskScoreResponse)
@limiter.limit(tenant_rate_limit)
def calculate_risk_api(
    request: Request,
    payload: RiskScoreRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):  
    # Query tenant risk state once and reuse it
    tenant_risk_state = (
        db.query(TenantRiskState)
        .filter(TenantRiskState.tenant_id == tenant.tenant_id)
        .first()
    )
    
    enforce_risk_policy(db, tenant.tenant_id, tenant_risk_state)
    enforce_tenant_policy(db, tenant.tenant_id, tenant_risk_state)
    try:
        data = payload.dict()
        data["company_size"] = COMPANY_SIZE_MAP.get(data["company_size"], 0)

        decision = calculate_risk(data, version="v1.2")
        redis_client.setex(f"risk_score:{tenant.tenant_id}", 300, decision.score)

        assessment = RiskAssessment(
            tenant_id=tenant.tenant_id,
            company_size=payload.company_size,
            industry=payload.industry,
            has_gst=payload.has_gst,
            has_pan=payload.has_pan,
            risk_score=decision.score,
            risk_level=decision.level,
            reasons=json.dumps(decision.reasons),
            ruleset_version="v1.2",
        )

        db.add(assessment)
        db.commit()

        emit_event(
            event_type="risk_score_generated",
            tenant_id=tenant.tenant_id,
            payload={
                "endpoint": "/api/public/risk/score",
                "risk_score": decision.score,
                "risk_level": decision.level,
                "ruleset_version": "v1.2",
            },
        )

        return {
            "risk_score": decision.score,
            "risk_level": decision.level,
            "reasons": decision.reasons,
        }
    except Exception as e:
        db.rollback()
        raise
@router.get("/history", response_model=list[RiskScoreOut])
def get_risk_history(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return (
        db.query(RiskAssessment)
        .filter(RiskAssessment.tenant_id == tenant.tenant_id)
        .order_by(RiskAssessment.created_at.desc())
        .all()
    )
@router.post("/trace")
def risk_trace(
    request: Request,
    payload: RiskScoreRequest,
    tenant: Tenant = Depends(get_current_tenant),
):
    try:
        data = payload.dict()
        data["company_size"] = COMPANY_SIZE_MAP.get(data["company_size"], 0)

        decision = calculate_risk(
            data,
            version="v1.2",
        )
        redis_client.setex(f"risk_score:{tenant.tenant_id}", 300, decision.score)
        
        rules_fired = []
        if hasattr(decision, 'rules_fired') and decision.rules_fired:
            rules_fired = [
                {"rule": r.rule, "points": r.points}
                for r in decision.rules_fired
            ]
        
        return {
            "version": "v1.2",
            "risk_score": decision.score,
            "risk_level": decision.level,
            "reasons": decision.reasons,
            "rules_fired": rules_fired,
            "evaluated_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise


