try:
    from scripts._bootstrap import add_project_root
except ModuleNotFoundError:
    from _bootstrap import add_project_root

add_project_root()

from app.db.database import SessionLocal
from app.models.governance_alert import GovernanceAlert


def main():
    db = SessionLocal()
    try:
        existing = (
            db.query(GovernanceAlert)
            .filter(GovernanceAlert.tenant_id == "demo")
            .filter(GovernanceAlert.alert_type == "event_spike_detected")
            .filter(GovernanceAlert.message == "test alert")
            .first()
        )
        if existing:
            print("Test governance alert already exists.")
            return

        alert = GovernanceAlert(
            tenant_id="demo",
            alert_type="event_spike_detected",
            severity="warning",
            message="test alert",
        )
        db.add(alert)
        db.commit()
        print("Test governance alert inserted for tenant demo.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
