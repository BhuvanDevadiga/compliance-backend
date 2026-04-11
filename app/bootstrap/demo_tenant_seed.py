from app.core.security import hash_api_key
from app.db.database import SessionLocal
from app.models.tenant import Tenant
from app.models.tenant_api_key import TenantAPIKey


TENANT_ID = "demo"
API_KEY = "sk_demo_123"


def main() -> None:
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.tenant_id == TENANT_ID).first()
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
            db.add(
                TenantAPIKey(
                    tenant_id=TENANT_ID,
                    key_hash=api_key_hash,
                    name="demo-key",
                    is_active=True,
                )
            )

        db.commit()
        print("Demo tenant created/updated")
    finally:
        db.close()


if __name__ == "__main__":
    main()
