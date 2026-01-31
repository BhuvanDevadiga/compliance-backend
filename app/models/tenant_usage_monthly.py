from sqlalchemy import Column, Integer, String, DateTime, func, UniqueConstraint
from app.db.base import Base


class TenantUsageMonthly(Base):
    __tablename__ = "tenant_usage_monthly"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)

    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    path = Column(String, nullable=False)
    method = Column(String, nullable=False)

    request_count = Column(Integer, default=0)
    last_seen = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "year", "month", "path", "method",
            name="uq_tenant_monthly_usage"
        ),
    )
