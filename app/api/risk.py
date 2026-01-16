import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.risk import RiskScoreRequest, RiskScoreResponse, RiskScoreOut
from app.services.risk_rules.registry import calculate_risk
from app.db.session import get_db
from app.models.risk import RiskAssessment

router = APIRouter(tags=["Risk"])
@router.get("/history", response_model=List[RiskScoreOut])
def get_risk_history(db: Session = Depends(get_db)):
    return db.query(RiskAssessment).order_by(RiskAssessment.created_at.desc()).all()


@router.post("/score", response_model=RiskScoreResponse)
def calculate_risk_api(
    payload: RiskScoreRequest,
    db: Session = Depends(get_db)
):
    risk_score, risk_level, reasons = calculate_risk(payload.dict(), version="v1.0")

    assessment = RiskAssessment(
        company_size=payload.company_size,
        industry=payload.industry,
        has_gst=payload.has_gst,
        has_pan=payload.has_pan,
        risk_score=risk_score,
        risk_level=risk_level,
        reasons=json.dumps(reasons), 
        ruleset_version="v1.0",
    )

    db.add(assessment)
    db.commit()

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "reasons": reasons,
    }
