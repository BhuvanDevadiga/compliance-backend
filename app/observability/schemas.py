from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditEvent(BaseModel):
    request_id: str
    timestamp: datetime

    tenant_id: Optional[str]
    api_key_hash: Optional[str]

    method: str
    path: str
    status_code: int
    latency_ms: int

    ip_address: Optional[str]
    user_agent: Optional[str]

    request_hash: Optional[str]
    response_size: Optional[int]
