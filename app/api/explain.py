from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.decision_explainer import explain_decision

router = APIRouter(prefix="/api/risk", tags=["Risk Explainability"])


@router.get("/explain/{decision_id}")
def explain_risk_decision(decision_id: int, db: Session = Depends(get_db)):
    return explain_decision(db, decision_id)