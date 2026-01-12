from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.risk import RiskScoreRequest, RiskScoreResponse
from app.db.session import get_db
from app.models.risk import RiskAssessment

router = APIRouter()


@router.post("/score", response_model=RiskScoreResponse)
def calculate_risk(
    payload: RiskScoreRequest,
    db: Session = Depends(get_db)
):
    
    risk_score = 50
    risk_level = "MEDIUM"

    
    assessment = RiskAssessment(
        company_size=payload.company_size,
        industry=payload.industry,
        has_gst=payload.has_gst,
        has_pan=payload.has_pan,
        risk_score=risk_score,
        risk_level=risk_level,
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return RiskScoreResponse(
        risk_score=risk_score,
        risk_level=risk_level
    )

from typing import List
from app.schemas.risk import RiskScoreOut


@router.get("/scores", response_model=List[RiskScoreOut])
def get_risk_scores(db: Session = Depends(get_db)):
    return db.query(RiskAssessment).all()
