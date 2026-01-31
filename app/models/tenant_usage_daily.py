from sqlalchemy import Column, Integer, String, Date, DateTime, UniqueConstraint
from app.db.base import Base
from datetime import datetime


class TenantUsageDaily(Base):
    __tablename__ = "tenant_usage_daily"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)

    path = Column(String, nullable=False)
    method = Column(String, nullable=False)

    usage_date = Column(Date, nullable=False)

    request_count = Column(Integer, default=0)
    last_seen = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "path",
            "method",
            "usage_date",
            name="uq_tenant_usage_daily"
        ),
    )
