import secrets
from app.core.security import hash_api_key
from app.models.tenant_api_key import TenantAPIKey

def generate_api_key():
    return secrets.token_urlsafe(32)

def create_api_key(db, tenant_id: str, name:str = None):
    raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)

    key = TenantAPIKey(
        tenant_id = tenant_id,
        key_hash = key_hash,
        name = name,
    )
    db.add(key)
    db.flush()

    return raw_key


def revoke_api_key(key: TenantAPIKey) -> None:
    key.is_active = False
