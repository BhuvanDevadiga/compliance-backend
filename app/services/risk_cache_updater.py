from app.core.redis_client import redis_client
from app.services.escalation_probability_engine import get_score

def update_risk_score(tenant_id: str):
    score = get_score(tenant_id)
    redis_client.setex(f"risk_score:{tenant_id}", 300, score)