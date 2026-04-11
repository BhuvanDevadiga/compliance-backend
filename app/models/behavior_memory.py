from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class BehaviorMemory(Base):

    __tablename__ = "behavior_memory"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(String, index=True, nullable=False)

    behavior_score = Column(Float, nullable=False)
    volatility = Column(String, nullable=False)
    classification = Column(String, nullable=False)

    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return (
            f"<BehaviorMemory tenant={self.tenant_id} "
            f"score={self.behavior_score} "
            f"class={self.classification}>"
        )
