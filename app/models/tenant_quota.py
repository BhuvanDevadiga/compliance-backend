from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base


class TenantQuota(Base):
    __tablename__ = "tenant_quotas"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, unique=True, nullable=False)

    plan = Column(String, nullable=False, default="free")

    daily_limit = Column(Integer, nullable=False)
    monthly_limit = Column(Integer, nullable=False)

    
    enforce_hard_limit = Column(Boolean, nullable=False, default=True)
