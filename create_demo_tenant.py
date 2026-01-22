from app.db.database import SessionLocal
from app.models.tenant import Tenant
import secrets

db = SessionLocal()

tenant = Tenant(
    name="Demo Company",
    tenant_id=secrets.token_hex(8),
    api_key=secrets.token_hex(16),
)

db.add(tenant)
db.commit()

print("✅ Demo tenant created")
print("Tenant ID:", tenant.tenant_id)
print("API Key:", tenant.api_key)
