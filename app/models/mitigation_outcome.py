from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class MitigationOutcome(Base):
    __tablename__ = "mitigation_outcomes"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(String, index=True, nullable=False)
    mitigation_action = Column(String, nullable=False)

    behavior_improved = Column(Boolean, nullable=False)

    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
