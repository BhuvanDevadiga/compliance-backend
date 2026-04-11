from app.db.database import SessionLocal
from app.models.tenant import Tenant
from app.models.tenant_api_key import TenantAPIKey
from app.core.security import hash_api_key
from app.services.api_key_service import generate_api_key


db = SessionLocal()

tenant_id = "demo"

raw_key = generate_api_key()
key_hash = hash_api_key(raw_key)

tenant = db.query(Tenant).filter_by(tenant_id=tenant_id).first()
if not tenant:
    tenant = Tenant(
        name="Demo Company",
        tenant_id=tenant_id,
        api_key_hash=key_hash,
    )
    db.add(tenant)
    db.flush()

key = TenantAPIKey(
    tenant_id=tenant.tenant_id,
    key_hash=key_hash,
    name="demo-key",
)
db.add(key)
db.commit()

print("Demo tenant ready")
print("Tenant ID:", tenant.tenant_id)
print("API Key:", raw_key)