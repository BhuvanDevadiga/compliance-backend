from sqlalchemy import Column, String, Boolean, DateTime
from app.db.base import Base
from datetime import datetime


class TenantSystemState(Base):
    __tablename__ = "tenant_system_state"

    tenant_id = Column(String, primary_key=True, index=True)

    adaptive_engine_frozen = Column(Boolean, default=False)
    freeze_reason = Column(String, nullable=True)
    freeze_locked_version = Column(String, nullable=True)
    frozen_at = Column(DateTime, nullable=True)
    last_updated_at = Column(DateTime, default=datetime.utcnow)