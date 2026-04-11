from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class TenantAPIKey(Base):
    __tablename__ = "tenant_api_keys"

    id = Column(Integer, primary_key=True)

    tenant_id = Column(
        String,
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    key_hash = Column(String, unique=True, nullable=False)

    name = Column(String, nullable=True)  

    is_active = Column(Boolean, default=True, nullable=False)

    expires_at = Column(DateTime(timezone=True), nullable=True)

    last_used_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())