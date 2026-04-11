from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base


class UsageCounter(Base):
    __tablename__ = "usage_counters"

    id = Column(Integer, primary_key=True)

    tenant_id = Column(String, nullable=False, index=True)

    period_type = Column(String, nullable=False)  
    # "hour" | "day" | "month"

    period_key = Column(String, nullable=False)
    # examples:
    # 2026-02-06-14
    # 2026-02-06
    # 2026-02

    count = Column(Integer, nullable=False, default=0)

    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("tenant_id", "period_type", "period_key"),
    )
