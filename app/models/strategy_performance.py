from sqlalchemy import Column, String, Float, DateTime
from app.db.base import Base
from datetime import datetime


class StrategyPerformance(Base):
    __tablename__ = "strategy_performance"

    tenant_id = Column(String, primary_key=True, index=True)
    strategy_name = Column(String, primary_key=True)

    success_score = Column(Float, default=0.0)
    failure_score = Column(Float, default=0.0)

    last_updated = Column(DateTime, default=datetime.utcnow)
    confidence = Column(Float, default=0.5)
    short_term_success = Column(Float, default=0)
    short_term_failure = Column(Float, default=0)
