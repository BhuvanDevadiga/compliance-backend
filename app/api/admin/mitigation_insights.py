from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.mitigation_analytics import mitigation_summary

router = APIRouter(prefix="/api/admin", tags=["Admin Insights"])


@router.get("/mitigation/insights")
def mitigation_insights(db: Session = Depends(get_db)):
    return mitigation_summary(db)
