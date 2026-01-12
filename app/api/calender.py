from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.model import User
from app.services.complnaince_calender import generate_compliance_calendar
from app.services.compliance_persist import persist_compliance_calendar

router = APIRouter(prefix="/calendar", tags=["Compliance Calendar"])

@router.get("/{user_id}")
def get_calendar(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "User not found"}

    user_dict = {
        "id": user.id,
        "gst_registered": user.gst_registered,
        "has_employees_or_contractors": user.has_employees_or_contractors
    }

    calendar = generate_compliance_calendar(user_dict)
    return {"calendar": calendar}

@router.post("/{user_id}/generate")
def generate_and_save_calendar(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "User not found"}

    user_dict = {
        "id": user.id,
        "gst_registered": user.gst_registered,
        "has_employees_or_contractors": user.has_employees_or_contractors
    }

    calendar = generate_compliance_calendar(user_dict)

    saved = persist_compliance_calendar(
        db=db,
        user_id=user.id,
        calendar=calendar
    )

    return {
        "message": "Compliance calendar generated & saved",
        "count": len(saved)
    }

from app.model import UserCompliance
from datetime import date

@router.get("/{user_id}")
def get_upcoming_compliances(
    user_id: int,
    db: Session = Depends(get_db)
):
    today = date.today()

    compliances = (
        db.query(UserCompliance)
        .filter(
            UserCompliance.user_id == user_id,
            UserCompliance.due_date >= today,
            UserCompliance.status == "PENDING"
        )
        .order_by(UserCompliance.due_date)
        .all()
    )

    return compliances
