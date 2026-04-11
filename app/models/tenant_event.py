from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime

from app.db.base import Base


class TenantEvent(Base):

    __tablename__ = "tenant_events"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(String, index=True)
    event_type = Column(String, index=True)

    payload = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
