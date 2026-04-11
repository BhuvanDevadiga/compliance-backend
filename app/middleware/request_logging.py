import hashlib
import json
import logging
import os
import time
import uuid
from fastapi import Request

from app.core.redis_client import redis_client

logger = logging.getLogger("app.request")

async def request_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    tenant_id = request.headers.get("X-Tenant-ID")
    api_key = request.headers.get("X-API-Key")
    signature = request.headers.get("X-Signature")
    signature_required = os.getenv("SIGNATURE_REQUIRED", "false").lower() in ("1", "true", "yes", "on")
    header_anomaly = 0

    if not tenant_id:
        header_anomaly = 1
    elif not api_key or len(api_key) < 32:
        header_anomaly = 1
    elif signature_required and not signature:
        header_anomaly = 1

    logger.info(
        "Request processed",
        extra={
            "request_id": request_id,
            "tenant_id": tenant_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(process_time, 2),
        },
    )

    if api_key:
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
        now = int(time.time())
        event = {
            "endpoint": request.url.path,
            "payload_size": int(request.headers.get("content-length", 0)),
            "latency": process_time,
            "status": response.status_code,
            "hour": time.localtime().tm_hour,
            "header_anomaly": header_anomaly,
        }
        key = f"api_key_events:{hashed_key}"

        redis_client.zadd(key, {json.dumps(event): now})

        seven_days_ago = now - (7 * 24 * 60 * 60)
        redis_client.zremrangebyscore(key, 0, seven_days_ago)

    return response
