import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.risk import RiskScoreRequest, RiskScoreResponse, RiskScoreOut
from app.services.risk_rules.registry import calculate_risk
from app.db.session import get_db
from app.models.risk import RiskAssessment
from datetime import datetime
from app.services.risk_rules.registry import calculate_risk

router = APIRouter(tags=["Risk"])

@router.get("/history", response_model=List[RiskScoreOut])
def get_risk_history(db: Session = Depends(get_db)):
    return db.query(RiskAssessment).order_by(RiskAssessment.created_at.desc()).all()


@router.post("/score", response_model=RiskScoreResponse)
def calculate_risk_api(
    payload: RiskScoreRequest,
    db: Session = Depends(get_db)
):
    decision = calculate_risk(payload.dict(), version="v1.2")

    assessment = RiskAssessment(
        company_size=payload.company_size,
        industry=payload.industry,
        has_gst=payload.has_gst,
        has_pan=payload.has_pan,
        risk_score=decision.score,
        risk_level=decision.level,
        reasons=json.dumps(decision.reasons), 
        ruleset_version="v1.0",
    )

    db.add(assessment)
    db.commit()

    return {
        "risk_score": decision.score,
        "risk_level": decision.level,
        "reasons": decision.reasons,
    }
@router.post("/trace", response_model=None)
def risk_trace(payload: RiskScoreRequest):
    decision = calculate_risk(payload.dict(), version="v1.2")

    return {
        "version": "v1.2",
        "risk_score": decision.score,
        "risk_level": decision.level,
        "reasons": decision.reasons,
        "rules_fired": [
            {"rule": r.rule, "points": r.points}
            for r in decision.rules_fired
        ],
        "evaluated_at": datetime.utcnow().isoformat()
    }