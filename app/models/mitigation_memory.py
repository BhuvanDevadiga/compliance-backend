from sqlalchemy import Column, String, Float, Integer
from app.db.base import Base

class MitigationMemory(Base):
    __tablename__ = "mitigation_memory"
    mitigation_type = Column(String, primary_key=True)
    times_used = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    avg_probability_delta = Column(Float, default=0.0)
    reinforcement_score = Column(Float, default=0.0)
    tenant_id = Column(String, primary_key=True)