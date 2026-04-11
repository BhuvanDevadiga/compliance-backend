from sqlalchemy import Column, Integer, Float, String
from app.db.base import Base


class MitigationStrategyPerformance(Base):
    __tablename__ = "mitigation_strategy_performance"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, index=True)
    strategy = Column(String, index=True)

    success_score = Column(Float, default=1.0)
    failure_score = Column(Float, default=1.0)
    confidence = Column(Float, default=1.0)
    short_term_success = Column(Float, default=0.0)
    short_term_failure = Column(Float, default=0.0)
