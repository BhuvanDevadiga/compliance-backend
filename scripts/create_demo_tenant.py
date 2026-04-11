try:
    from scripts._bootstrap import add_project_root
except ModuleNotFoundError:
    from _bootstrap import add_project_root

add_project_root()

from app.db.database import SessionLocal
from app.models.tenant import Tenant
from app.models.tenant_api_key import TenantAPIKey
from app.core.security import hash_api_key

db = SessionLocal()

TENANT_ID = "demo"
API_KEY = "sk_demo_123"

try:
    tenant = (
        db.query(Tenant)
        .filter(Tenant.tenant_id == TENANT_ID)
        .first()
    )

    api_key_hash = hash_api_key(API_KEY)

    if tenant is None:
        tenant = Tenant(
            tenant_id=TENANT_ID,
            name="Demo Tenant",
            api_key_hash=api_key_hash,
            plan="pro",
            is_active=True,
        )
        db.add(tenant)
    else:
        tenant.name = "Demo Tenant"
        tenant.plan = "pro"
        tenant.is_active = True
        tenant.api_key_hash = api_key_hash

    key_record = (
        db.query(TenantAPIKey)
        .filter(
            TenantAPIKey.tenant_id == TENANT_ID,
            TenantAPIKey.key_hash == api_key_hash,
        )
        .first()
    )

    if key_record is None:
        key_record = TenantAPIKey(
            tenant_id=TENANT_ID,
            key_hash=api_key_hash,
            name="demo-key",
            is_active=True,
        )
        db.add(key_record)

    db.commit()
    print("Demo tenant created/updated")
finally:
    db.close()
