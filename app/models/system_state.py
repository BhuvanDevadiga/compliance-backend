from sqlalchemy import Column, Boolean, String, DateTime
from app.db.base import Base
from datetime import datetime

class GlobalSystemState(Base):
    __tablename__ = "global_system_state"

    id = Column(String, primary_key=True, default="GLOBAL")

    adaptive_engine_frozen = Column(Boolean, default=False)
    freeze_reason = Column(String, nullable=True)
    frozen_at = Column(DateTime, nullable=True)
    freeze_locked_version = Column(String, nullable = True)
    platform_override_active = Column(Boolean, default=False)
    platform_override_reason = Column(String, nullable=True)
    platform_override_locked_version = Column(String, nullable=True)
    platform_override_activated_at = Column(DateTime, nullable=True) 