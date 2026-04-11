from pydantic import BaseModel
from typing import List
from datetime import datetime

class RiskDistribution(BaseModel):
    high: int
    medium: int
    low: int

class TopRiskItem(BaseModel):
    control_id: str
    risk_score: float
    risk_level: str

class DashboardSummaryResponse(BaseModel):
    tenant_id: str
    total_controls: int
    audit_readiness: float
    average_risk: float
    distribution: RiskDistribution
    top_risks: List[TopRiskItem]
    last_updated: datetime | None
