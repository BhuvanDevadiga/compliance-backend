from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.risk import RiskScoreRequest, RiskScoreResponse
from app.services.risk_engine import calculate_risk_score
from app.db.session import get_db
from app.models.risk import RiskAssessment
import json

router = APIRouter(prefix="/api/risk", tags=["Risk"])

@router.post("/score", response_model=RiskScoreResponse)
def calculate_risk(payload: RiskScoreRequest, db: Session = Depends(get_db)):
    try:
        risk_score, risk_level, reasons = calculate_risk_score(payload)

        assessment = RiskAssessment(
            company_size=payload.company_size,
            industry=payload.industry,
            has_gst=payload.has_gst,
            has_pan=payload.has_pan,
            risk_score=risk_score,
            risk_level=risk_level,
            reasons=json.dumps(reasons)
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return RiskScoreResponse(
            risk_score=risk_score,
            risk_level=risk_level,
            reasons=reasons
        )

    except Exception:
        raise HTTPException(status_code=500, detail="Internal risk engine error")

@router.get("/history", response_model=List[RiskScoreResponse])
def get_risk_history(db: Session = Depends(get_db)):
    assessments = db.query(RiskAssessment).all()
    return [
        RiskScoreResponse(
            risk_score=a.risk_score,
            risk_level=a.risk_level,
            reasons=json.loads(a.reasons) if isinstance(a.reasons, str) else a.reasons
        )
        for a in assessments
    ]

