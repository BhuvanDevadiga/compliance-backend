from sqlalchemy.orm import Session
from datetime import date, timedelta
from app.model import UserCompliance

def build_compliance_context(db: Session, user_id: int):
    today = date.today()
    next_7_days = today + timedelta(days=7)

    pending = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "PENDING"
    ).all()

    missed = db.query(UserCompliance).filter(
        UserCompliance.user_id == user_id,
        UserCompliance.status == "MISSED"
    ).all()

    upcoming = [
        c for c in pending
        if today <= c.due_date <= next_7_days
    ]

    context = {
        "today": str(today),
        "pending_count": len(pending),
        "missed_count": len(missed),
        "upcoming": [
            {
                "code": c.compliance_code,
                "due_date": str(c.due_date)
            }
            for c in upcoming
        ]
    }

    return context

def build_prompt(context: dict, user_query: str):
    return f"""
You are a compliance assistant for Indian SMEs.

Today's date: {context['today']}

Pending compliances: {context['pending_count']}
Missed compliances: {context['missed_count']}

Upcoming deadlines (next 7 days):
{context['upcoming']}

User question:
"{user_query}"

Answer clearly, concisely, and in business language.
"""
