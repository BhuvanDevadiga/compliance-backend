from datetime import datetime
from sqlalchemy.orm import Session
from app.model import UserCompliance

def persist_compliance_calendar(
    db: Session,
    user_id: int,
    calendar: list
):
    """
    Persist generated compliance calendar into DB.
    Idempotent: avoids duplicates, updates existing entries.
    """

    saved_entries = []

    for item in calendar:
        due_date = datetime.fromisoformat(item["due_date"]).date()

        existing = (
            db.query(UserCompliance)
            .filter(
                UserCompliance.user_id == user_id,
                UserCompliance.compliance_code == item["code"],
                UserCompliance.due_date == due_date
            )
            .first()
        )

        if existing:
            # Update type if needed (safe update)
            existing.compliance_type = item["type"]
            saved_entries.append(existing)
        else:
            new_entry = UserCompliance(
                user_id=user_id,
                compliance_code=item["code"],
                compliance_type=item["type"],
                due_date=due_date,
                status="PENDING"
            )
            db.add(new_entry)
            saved_entries.append(new_entry)

    db.commit()
    return saved_entries
