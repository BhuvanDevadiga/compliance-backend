from sqlalchemy.orm import Session
from datetime import datetime
from packaging import version
from app.models.system_state import GlobalSystemState
from app.core.engine_config import ENGINE_VERSION

def get_global_state(db: Session):
    state = db.query(GlobalSystemState).first()
    return state

def activate_platform_override(db: Session, reason: str):
    state = get_global_state(db)

    state.platform_override_active = True
    state.platform_override_reason = reason 
    state.platform_override_locked_version = ENGINE_VERSION
    state.platform_override_activated_at = datetime.utcnow()

    db.commit()

    print("🚨 PLATFORM OVERRIDE ACTIVATED")

def attempt_platform_unfreeze(db: Session):
    state = get_global_state(db)

    if not state.platform_override_active:
        return True

    if version.parse(ENGINE_VERSION)> version.parse(state.platform_override_locked_version):
        state.platform_override_active = False
        state.platform_override_reason = f"Unlocked via version bump to {ENGINE_VERSION}"
        state.platform_override_locked_version = None
        state.platform_override_activated_at = None
        db.commit()

        print("✅ PLATFORM OVERRIDE LIFTED")
        return True
    return False   

# Backwards-compatible aliases for earlier misspelled function names.
def activate_plateform_override(db: Session, reason: str):
    return activate_platform_override(db, reason)

def attempt_plateform_unfreeze(db: Session):
    return attempt_platform_unfreeze(db)
