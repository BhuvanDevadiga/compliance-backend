from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)

    api_key = Column(String, unique=True, nullable=False, index=True)

    is_active = Column(Boolean, default=True)
    plan = Column(String, default="free")  # free | pro | enterprise

    created_at = Column(DateTime(timezone=True), server_default=func.now())

