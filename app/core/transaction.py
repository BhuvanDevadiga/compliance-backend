import time
import logging
from collections import defaultdict, deque
from sqlalchemy.exc import OperationalError
from psycopg2.errors import DeadlockDetected, SerializationFailure
from app.services.governance_alert_service import create_alert

MAX_RETRIES = 3
BASE_BACKOFF = 0.05  # 50ms
RETRY_ALERT_THRESHOLD = 5
RETRY_ALERT_WINDOW_SECONDS = 60

logger = logging.getLogger("transaction")

_retry_tracker = defaultdict(deque)


def _track_retry_and_alert(db, tenant_id: str):
    now = time.monotonic()
    window_start = now - RETRY_ALERT_WINDOW_SECONDS
    events = _retry_tracker[tenant_id]

    while events and events[0] < window_start:
        events.popleft()

    events.append(now)

    if len(events) == RETRY_ALERT_THRESHOLD:
        try:
            create_alert(
                db,
                tenant_id,
                "excessive_lock_contention",
                "warning",
                "High retry rate detected for tenant. "
                "Potential hot tenant, abuse, misconfiguration, or attack attempt.",
            )
            db.commit()
        except Exception as alert_error:
            db.rollback()
            logger.warning(
                f"[TX RETRY ALERT] failed to record alert for tenant={tenant_id} "
                f"error={type(alert_error).__name__}"
            )

def run_in_transaction(db_factory, fn, *args, **kwargs):
  

    for attempt in range(1, MAX_RETRIES + 1):
        db = db_factory()

        try:
            with db.begin():
                return fn(db, *args, **kwargs)

        except OperationalError as e:
            db.rollback()

            # Check for Postgres deadlock / serialization
            orig = getattr(e, "orig", None)

            if isinstance(orig, (DeadlockDetected, SerializationFailure)):
                logger.warning(
                    f"[TX RETRY] attempt={attempt} reason={type(orig).__name__}"
                )
                tenant_id = kwargs.get("tenant_id")
                if tenant_id and attempt > 1:
                    _track_retry_and_alert(db, tenant_id)
                if attempt == MAX_RETRIES:
                    logger.error("[TX FAILED] Max retries exceeded")
                    raise

                sleep_time = BASE_BACKOFF * attempt
                time.sleep(sleep_time)
                continue

            raise

        finally:
            db.close()
