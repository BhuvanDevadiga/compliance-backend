# app/background/profiler_worker.py

import threading
import time
from datetime import datetime

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.core.transaction import run_in_transaction
from app.models.tenant import Tenant
from app.services.tenant_profiler import generate_profile
from app.services.anomaly_detector import detect_anomalies

POLL_INTERVAL_SECONDS = 60  # Run every 1 minute

def profiler_loop():
    """
    Background loop to profile all tenants and detect anomalies.
    """
    while True:
        db: Session = SessionLocal()
        try:
            tenants = db.query(Tenant).all()
        finally:
            db.close()

        now = datetime.utcnow()

        for tenant in tenants:
            tenant_id = tenant.tenant_id

            # Generate profile
            try:
                run_in_transaction(SessionLocal, generate_profile, tenant_id=tenant_id)
            except Exception as e:
                print(f"[{now}] Profiler error for tenant {tenant_id}: {e}")

            # Detect anomalies
            try:
                run_in_transaction(SessionLocal, detect_anomalies, tenant_id=tenant_id)
            except Exception as e:
                print(f"[{now}] Anomaly detection error for tenant {tenant_id}: {e}")

        time.sleep(POLL_INTERVAL_SECONDS)


def start_profiler_worker():
    """
    Start profiler in a daemon thread.
    """
    thread = threading.Thread(target=profiler_loop, daemon=True)
    thread.start()
    print("Tenant profiler worker started...")
