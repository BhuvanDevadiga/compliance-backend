import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from slowapi.util import get_remote_address
from slowapi import _rate_limit_exceeded_handler

from app.schemas.risk import RiskScoreRequest, RiskScoreResponse, RiskScoreOut
from app.core.redis_client import redis_client
from app.services.risk_rules.registry import calculate_risk
from app.db.session import get_db
from app.core.auth import get_current_tenant
from app.core.rate_limiter import limiter, tenant_rate_limit
from app.models.tenant import Tenant
from app.models.risk_assessment import RiskAssessment


COMPANY_SIZE_MAP = {
    "micro": 1,
    "small": 5,
    "medium": 50,
    "large": 250,
}

router = APIRouter(
    
    tags=["Risk"],
    dependencies=[Depends(get_current_tenant)],
)


@router.get("/history", response_model=List[RiskScoreOut])
def get_risk_history(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    return (
        db.query(RiskAssessment)
        .filter(RiskAssessment.tenant_id == tenant.tenant_id)
        .order_by(RiskAssessment.created_at.desc())
        .all()
    )


@router.post("/score", response_model=RiskScoreResponse)
@limiter.limit(tenant_rate_limit)
def calculate_risk_api(
    request: Request,
    payload: RiskScoreRequest,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    normalized_payload = payload.dict()
    normalized_payload["company_size"] = COMPANY_SIZE_MAP[payload.company_size]

    decision = calculate_risk(
        normalized_payload,
        version="v1.2"
    )
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


    return {
        "risk_score": decision.score,
        "risk_level": decision.level,
        "reasons": decision.reasons,
    }


@router.post("/trace")
def risk_trace(
    request: Request,
    payload: RiskScoreRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    normalized_payload = payload.dict()
    normalized_payload["company_size"] = COMPANY_SIZE_MAP[payload.company_size]

    decision = calculate_risk(
        normalized_payload,
        version="v1.2"
    )
    redis_client.setex(f"risk_score:{tenant.tenant_id}", 300, decision.score)

    return {
        "version": "v1.2",
        "risk_score": decision.score,
        "risk_level": decision.level,
        "reasons": decision.reasons,
        "rules_fired": [
            {"rule": r.rule, "points": r.points}
            for r in decision.rules_fired
        ],
        "evaluated_at": datetime.utcnow().isoformat(),
    }

    ...
