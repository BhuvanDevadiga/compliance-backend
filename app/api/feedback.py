from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.feedback_service import record_feedback

router = APIRouter(prefix ="/api/feedback", tags =["Feedback"])

@router.post("/decision")
def submit_feedback(
    decision_id: int,
    tenant_id: str,
    outcome: str,
    db: Session = Depends(get_db)
):
    return record_feedback(db, decision_id, tenant_id, outcome)