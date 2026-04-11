from datetime import UTC, datetime, timedelta
import random
import uuid

try:
    from scripts._bootstrap import add_project_root
except ModuleNotFoundError:
    from _bootstrap import add_project_root

add_project_root()

from app.db.database import SessionLocal
from app.models.control import Control
from app.models.tenant import Tenant


def main():
    db = SessionLocal()
    tenant_id = "demo"

    try:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == tenant_id).first()
        if tenant is None:
            print("Demo tenant not found. Run scripts/create_demo_tenant.py first.")
            return

        existing = db.query(Control).filter(Control.tenant_id == tenant_id).count()
        if existing > 0:
            print("Controls already seeded.")
            return

        now = datetime.now(UTC).replace(tzinfo=None)

        for i in range(25):
            control = Control(
                id=str(uuid.uuid4()),
                tenant_id=tenant_id,
                name=f"CC{i + 1}",
                framework="SOC2",
                last_evidence_updated_at=now - timedelta(days=random.randint(5, 120)),
                owner_last_login=now - timedelta(days=random.randint(1, 90)),
                historical_failure_rate=round(random.uniform(0, 0.4), 2),
                next_audit_date=now + timedelta(days=45),
            )
            db.add(control)

        db.commit()
        print("Seeded 25 controls for tenant demo.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
