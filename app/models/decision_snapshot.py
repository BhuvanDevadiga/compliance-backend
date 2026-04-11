from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.sql import func
from app.db.base import Base
import uuid

class DecisionSnapshot(Base):
    __tablename__ = "decision_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, index=True)

    risk_level = Column(String)
    context = Column(String)

    strategy_stats_json = Column(Text)
    selected_strategy = Column(String)

    regret = Column(Float)
    random_seed = Column(String)

    engine_version = Column(String)

    previous_hash = Column(String)
    current_hash = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())