from sqlalchemy import String, Column, Boolean, DateTime
from app.db.base import Base
from datetime import datetime

class GovernanceKey(Base):
    __tablename__ = "governance_keys"

    key_id = Column(String, primary_key=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
    encrypted_secret = Column(String, nullable=False)
