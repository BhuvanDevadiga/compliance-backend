import secrets
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.governance_key import GovernanceKey
from app.core.crypto_utils import encrypt_secret

def create_new_key(db: Session)-> GovernanceKey:
    key_id = f"key-{secrets.token_hex(4)}"
    secret = secrets.token_hex(32)

    new_key = GovernanceKey(
        key_id = key_id,
        encrypted_secret=encrypt_secret(secret),
        is_active = True
    ) 
    db.query(GovernanceKey).filter(
        GovernanceKey.is_active == True
    ).update({"is_active": False})

    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    return new_key

def get_active_key(db: Session) -> GovernanceKey:
    return db.query(GovernanceKey)\
        .filter(GovernanceKey.is_active == True)\
        .first()


def get_key_by_id(db: Session, key_id: str) -> GovernanceKey:
    return db.query(GovernanceKey)\
        .filter(GovernanceKey.key_id == key_id)\
        .first()


def revoke_key(db: Session, key_id: str):
    key = get_key_by_id(db, key_id)
    if key:
        key.is_active = False
        key.revoked_at = datetime.utcnow()
        db.commit()


def import_historical_keys(
    db: Session,
    keys: list[tuple[str, str]],
    created_at: datetime | None = None,
) -> int:
    """
    Import legacy governance keys so historical signatures can be verified.
    Keys are inserted as inactive and revoked to avoid re-use.
    """
    inserted = 0
    for key_id, secret in keys:
        if get_key_by_id(db, key_id):
            continue
        record = GovernanceKey(
            key_id=key_id,
            encrypted_secret=encrypt_secret(secret),
            is_active=False,
            created_at=created_at or datetime.utcnow(),
            revoked_at=datetime.utcnow(),
        )
        db.add(record)
        inserted += 1

    if inserted:
        db.commit()

    return inserted
