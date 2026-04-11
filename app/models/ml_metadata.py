from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.db.base import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class MLModelMetadata(Base):
    __tablename__ = "ml_model_metadata"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True, unique=True, nullable=True)
    model_version = Column(Integer, default=1)
    last_retrained_at = Column(DateTime, default=datetime.utcnow)
    confidence_decline_streak = Column(Integer, default=0)

    tenant = relationship("Tenant")
    drift_streak = Column(Integer, default=0)
