from pydantic import BaseModel
from typing import List


class TenantPulseResponse(BaseModel):
    tenant_id: str
    signals: List[str]
    health_delta: float
    drift_detected: bool
    strict_ratio: float
    governance_delta: float