import hashlib, hmac
from sqlalchemy.orm import Session
from app.services.key_management_service import get_active_key, get_key_by_id
from app.core.crypto_utils import decrypt_secret

def compute_event_hash(payload: str, previous_hash: str | None)-> str:
    combined = (payload + (previous_hash or "")).encode()
    return hashlib.sha256(combined).hexdigest()

def sign_hash(db: Session, event_hash: str) -> tuple[str, str]:

    key = get_active_key(db)

    if not key:
        raise Exception("No active governance key found.")
    
    secret = decrypt_secret(key.encrypted_secret)

    signature = hmac.new(
        secret.encode(),
        event_hash.encode(),
        hashlib.sha256
    ).hexdigest()

    return signature, key.key_id


def verify_signature(db: Session, event_hash: str, signature: str, key_id: str) -> bool:

    key = get_key_by_id(db, key_id)

    if not key:
        return False
    
    secret = decrypt_secret(key.encrypted_secret)

    expected = hmac.new(
        secret.encode(),
        event_hash.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
