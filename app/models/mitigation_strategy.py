from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from app.db.base import Base

class MitigationStrategy(Base):
    __tablename__ = "mitigation_strategy"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, index=True)
    strategy = Column(String)
    level = Column(String, index=True)
    total_plays = Column(Integer, default=0)
    total_reward = Column(Float, default=0.0)

    average_reward = Column(Float, default=0.0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    success_table = Column(Integer, default = 0)
    failure_table = Column(Integer, default= 0)
    success_volatility = Column(Integer, default = 0)
    failure_volatility = Column(Integer, default= 0)
    is_active = Column(Boolean, default = True)
    retired_at = Column(DateTime, nullable = True)
