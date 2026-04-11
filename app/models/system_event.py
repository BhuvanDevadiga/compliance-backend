from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, JSON, String

from app.db.base import Base


class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, nullable=True)

    event_type = Column(String, index=True)
    severity = Column(String, default="info")

    payload = Column(JSON)

    created_at = Column(DateTime, default=datetime.utcnow)
