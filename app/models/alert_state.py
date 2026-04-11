from sqlalchemy import Column, String, DateTime
from datetime import datetime

from app.db.base import Base


class AlertState(Base):
    __tablename__ = "alert_state"

    alert_key = Column(String, primary_key=True, index=True)
    last_emitted = Column(DateTime, default=datetime.utcnow)
