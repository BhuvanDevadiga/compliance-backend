from sqlalchemy import Column, Integer, String, Date, DateTime, func
from app.db.base import Base

class TenantUsage(Base):
    __tablename__ = "tenant_usage"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    path = Column(String, nullable=False)
    method = Column(String, nullable=False)
    usage_date = Column(Date, nullable=False)

    request_count = Column(Integer, default=1)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self):
        return (
            f"TenantUsage(id={self.id}, tenant_id={self.tenant_id}, "
            f"path={self.path}, method={self.method}, "
            f"request_count={self.request_count}, usage_date={self.usage_date})"
        )
