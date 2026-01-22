from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Literal, List


class RiskScoreRequest(BaseModel):
    company_size: str = Literal["micro", "small", "medium", "large"]
    industry: str = Field
    has_gst: bool
    has_pan: bool


class RiskScoreResponse(BaseModel):
    risk_score: int
    risk_level: str
    reasons: List[str]


class RiskScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    company_size: str
    industry: str
    has_gst: bool
    has_pan: bool
    risk_score: int
    risk_level: str
    created_at: datetime
  


