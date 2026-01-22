from app.db.database import SessionLocal
from app.models.tenant import Tenant

db = SessionLocal()

tenant = Tenant(
    tenant_id="demo",
    name="Demo Tenant",
    api_key="sk_demo_123",
    is_active=True,
)

db.add(tenant)
db.commit()

print("✅ Demo tenant created")

