from datetime import date, timedelta
from app.celery_app import celery_app
from app.database import SessionLocal
from app.model import UserCompliance

@celery_app.task
def daily_compliance_reminder():
    db = SessionLocal()
    today = date.today()

    upcoming = db.query(UserCompliance).filter(
        UserCompliance.status == "PENDING",
        UserCompliance.due_date <= today + timedelta(days=7)
    ).all()

    for compliance in upcoming:
        days_left = (compliance.due_date - today).days

        print(
            f"[REMINDER] User {compliance.user_id} | "
            f"{compliance.compliance_code} due in {days_left} day(s)"
        )

        if days_left < 0:
            compliance.status = "MISSED"

    db.commit()
    db.close()
