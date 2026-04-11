from sqlalchemy import Column, Integer, String, DateTime, Text, UniqueConstraint
from datetime import datetime
from app.db.base import Base


class GovernanceEventLog(Base):
    __tablename__ = "governance_event_log"
    __table_args__ = (
        UniqueConstraint("tenant_id", "event_hash", name="uq_tenant_event_hash"),
        UniqueConstraint("tenant_id", "previous_hash", name="uq_tenant_previous_hash"),
    )

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(String, nullable=True, index=True)
    event_type = Column(String, nullable=False)  # FREEZE, UNLOCK
    previous_version = Column(String, nullable=True)
    new_version = Column(String, nullable=True)

    reason = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    previous_hash = Column(String, nullable = True)
    event_hash = Column(String, nullable = True)
    signature = Column(String, nullable = True)
    signing_key_id = Column(String, nullable = True)
    original_payload = Column(Text, nullable=False)
