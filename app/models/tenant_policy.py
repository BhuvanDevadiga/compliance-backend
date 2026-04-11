from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.base import Base

class TenantPolicy(Base):
    __tablename__ = "tenant_policy"
    tenant_id = Column(String, primary_key=True, index=True)
    policy_name = Column(String, nullable=False)
    reason_snapshot = Column("rerason_snapshot", JSON, nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
