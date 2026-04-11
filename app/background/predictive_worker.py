import time
from app.db.database import SessionLocal
from app.core.transaction import run_in_transaction
from app.services.predictive_guard import predictive_guard


def predictive_loop():

    while True:

        run_in_transaction(SessionLocal, predictive_guard)

        time.sleep(30)


def start_predictive_worker():

    import threading

    thread = threading.Thread(
        target=predictive_loop,
        daemon=True,
    )
    thread.start()

    print("Predictive guard worker started...")
