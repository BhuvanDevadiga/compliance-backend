import logging
import threading
import time

from app.core.redis_client import redis_client
from app.db.database import SessionLocal
from app.ml.api_key_anomaly import analyze_key
from app.models.tenant import Tenant
from app.services.escalation_probability_engine import compute_escalation_probability

logger = logging.getLogger("app.risk_refresh")

REFRESH_INTERVAL_SECONDS = 300
LOCK_KEY = "risk_refresh_lock"
LOCK_TTL = 290

def acquire_lock():
    return redis_client.set(LOCK_KEY, "1", nx=True, ex=LOCK_TTL)

def refresh_all_tenants():
    db = SessionLocal()
    try:
        tenants = db.query(Tenant.tenant_id).all()
        for row in tenants:
            tenant_id = row[0]
            try:
                result = compute_escalation_probability(db, tenant_id, source="risk_refresh_scheduler")
                score = float(result.get("probability", 0.2))
                redis_client.setex(f"risk_score:{tenant_id}", 300, score)
                
            except Exception as e:
                logger.error("risk_refresh_error", extra={"tenant_id": tenant_id, "error": str(e)})

    finally:
        db.close()

def refresh_api_key_anomalies():
    keys = redis_client.keys("api_key_events:*")

    for key in keys:
        hashed_key = key.split(":", 1)[1]
        analyze_key(hashed_key)

def scheduler_loop():
    while True:
        try:
            if acquire_lock():
                logger.info("risk_scheduler_running")
                refresh_all_tenants()
                try:
                    refresh_api_key_anomalies()
                except Exception as e:
                    logger.error("api_key_anomaly_scheduler_error", extra={"error": str(e)})
        except Exception as e:
            logger.error("scheduler_error", extra={"error": str(e)})

        time.sleep(REFRESH_INTERVAL_SECONDS)


def start_scheduler():
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()        
