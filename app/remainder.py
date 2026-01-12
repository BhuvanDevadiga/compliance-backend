from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.model import UserCompliance

def check_due_compliances(db: Session):
    today = date.today()
    upcoming = today + timedelta(days=3)

    return db.query(UserCompliance).filter(
        UserCompliance.next_due_date <= upcoming,
        UserCompliance.status == "PENDING"
    ).all()
