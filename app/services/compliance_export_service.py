import json, hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.governance_event_log import GovernanceEventLog
from app.models.governance_anchor import GovernanceAnchor
from app.models.governance_key import GovernanceKey
from app.services.signing_service import verify_signature
from app.services.governance_service import sign_hash

def generate_compliance_bundle(db: Session):

    events = db.query(GovernanceEventLog).order_by(
        GovernanceEventLog.created_at.asc()
    ).all()

    anchors = db.query(GovernanceAnchor).order_by(
        GovernanceAnchor.anchored_at.asc()
    ).all()

    keys = db.query(GovernanceKey).all()

    # 🔐 Verify entire chain
    verification_status = "OK"

    for event in events:
        valid = verify_signature(
            db,
            event.event_hash,
            event.signature,
            event.signing_key_id
        )
        if not valid:
            verification_status = "FAILED"
            break

    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "system_version": "2.2",
        "verification_status": verification_status,
        "chain_head_hash": events[-1].event_hash if events else None,
        "governance_events": [
            {
                "id": e.id,
                "event_hash": e.event_hash,
                "previous_hash": e.previous_hash,
                "signature": e.signature,
                "signing_key_id": e.signing_key_id,
                "created_at": e.created_at.isoformat()
            } for e in events
        ],
        "anchors": [
            {
                "anchored_hash": a.anchored_hash,
                "anchor_source": a.anchor_source,
                "anchored_at": a.anchored_at.isoformat()
            } for a in anchors
        ],
        "signing_keys": [
            {
                "key_id": k.key_id,
                "created_at": k.created_at.isoformat(),
                "revoked_at": k.revoked_at.isoformat() if k.revoked_at else None
            } for k in keys
        ]
    }

    # 🔒 Compute bundle hash
    bundle_string = json.dumps(export_data, sort_keys=True)
    bundle_hash = hashlib.sha256(bundle_string.encode()).hexdigest()

    export_data["bundle_hash"] = bundle_hash

    signature, key_id = sign_hash(db, bundle_hash)

    export_data["signature"] = signature
    export_data["signing_key_id"] = key_id

    return export_data
