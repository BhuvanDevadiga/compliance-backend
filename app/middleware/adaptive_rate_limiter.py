import hashlib
import logging
import time

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.redis_client import redis_client

logger = logging.getLogger("app.rate_limit")

WINDOW_SECONDS = 60
DEFAULT_SCORE = 0.5

def map_score_to_limit(score: float) -> int:
    if score >= 0.8:
        return 20  
    elif score >= 0.5:
        return 60   
    else:
        return 200   
    

async def adaptive_rate_limiter(request: Request, call_next):
    tenant_id = request.headers.get("X-Tenant-ID")
    api_key = request.headers.get("X-API-Key")

    if not tenant_id:
        return await call_next(request)

    try:
        score_key = f"risk_score:{tenant_id}"
        cached_score =  redis_client.get(score_key)

        if not cached_score:
            score = DEFAULT_SCORE
        else:
            score = float(cached_score)

        limit = map_score_to_limit(score)
        if api_key:
            hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
            anomaly_flag = redis_client.get(f"api_key_anomaly:{hashed_key}")

            if anomaly_flag:
                limit = min(limit, 20)

        window_key = f"rate_limit:{tenant_id}:{int(time.time() // WINDOW_SECONDS)}"
        current = redis_client.incr(window_key)     

        if current == 1:
            redis_client.expire(window_key, WINDOW_SECONDS)

        if current > limit:
            logger.warning("rate_limit_exceeded",
                           extra={"tenant_id": tenant_id, "score": score, "limit": limit, "current": current})
            return JSONResponse(status_code=429, content={"detail": "Too Many Requests"})

    except Exception as e:
        logger.error("rate_limiter_error", extra={"error": str(e)})
            

    return await call_next(request)
