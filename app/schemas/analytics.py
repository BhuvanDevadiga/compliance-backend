from pydantic import BaseModel


class EndpointUsage(BaseModel):
    path: str
    request_count: int
    avg_latency_ms: float
