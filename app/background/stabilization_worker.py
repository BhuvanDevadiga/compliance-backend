import time
from app.db.database import SessionLocal
from app.core.transaction import run_in_transaction
from app.services.stabilization_engine import stabilize_tenants


def stabilization_loop():

    while True:

        run_in_transaction(SessionLocal, stabilize_tenants)

        time.sleep(60)


def start_stabilization_worker():

    import threading

    thread = threading.Thread(
        target=stabilization_loop,
        daemon=True,
    )
    thread.start()

    print("Stabilization worker started...")
