from sqlalchemy import Column, String, DateTime, Integer
from app.db.base import Base
from datetime import datetime

class GovernanceAnchor(Base):
    __tablename__ = "governance_anchors"

    id = Column(Integer, primary_key=True, index=True)
    anchored_hash = Column(String, nullable=False)
    anchor_source = Column(String, nullable=True)
    anchored_at = Column(DateTime, default=datetime.utcnow)