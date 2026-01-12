from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.database import get_db
from app.model import UserCompliance

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/{user_id}/summary")
def compliance_summary(user_id: int, db: Session = Depends(get_db)):
    total = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id
    ).count()

    pending = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "PENDING"
    ).count()

    filed = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "FILED"
    ).count()

    missed = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "MISSED"
    ).count()

    return {
        "total": total,
        "pending": pending,
        "filed": filed,
        "missed": missed
    }

@router.get("/{user_id}/upcoming")
def upcoming_compliances(user_id: int, db: Session = Depends(get_db)):
    today = date.today()
    next_week = today + timedelta(days=7)

    compliances = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "PENDING",
        UserCompliance.due_date.between(today, next_week)
    ).order_by(UserCompliance.due_date).all()

    return compliances

@router.get("/{user_id}/missed")
def missed_compliances(user_id: int, db: Session = Depends(get_db)):
    compliances = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "MISSED"
    ).order_by(UserCompliance.due_date.desc()).all()

    return compliances

