from app.db.database import SessionLocal
from app.models.tenant import Tenant

db = SessionLocal()
tenants = db.query(Tenant).all()

for t in tenants:
    print(t.id, t.tenant_id, t.api_key, t.is_active)

db.close()
