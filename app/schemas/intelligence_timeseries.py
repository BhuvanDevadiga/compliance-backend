from pydantic import BaseModel
from typing import List

class TimeseriesPoint(BaseModel):
    timestamp:str
    value:float

class TenantTimeseriesResponse(BaseModel):
    tenant_id:str
    health_index_trend: List[TimeseriesPoint]
    drift_trend: List[TimeseriesPoint]
    governance_trend: List[TimeseriesPoint]
    strict_ratio_trend: List[TimeseriesPoint]    