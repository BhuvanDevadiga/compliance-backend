import time

from app.db.database import SessionLocal
from app.core.transaction import run_in_transaction
from app.services.risk_decay import decay_risk


def risk_decay_loop():

    while True:

        run_in_transaction(SessionLocal, decay_risk)

        time.sleep(60)  # run every minute
