from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from datetime import datetime
from app.db.base import Base

class MLModelRetrainLog(Base):
    __tablename__ = "ml_model_retrain_logs"

    id = Column(Integer, primary_key=True, index=True)
    old_version = Column(Integer)
    new_version = Column(Integer)
    trigger_status = Column(String)
    streak_value = Column(Integer)
    samples = Column(Integer)
    strict_events = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    tenant_id = Column(String, ForeignKey("tenants.tenant_id"), index=True, nullable=True)
