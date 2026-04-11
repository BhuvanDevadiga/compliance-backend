from sqlalchemy.orm import Session
from datetime import datetime
from app.models.governance_event_log import GovernanceEventLog
from app.models.governance_anchor import GovernanceAnchor
import os

ANCHOR_FILE_PATH = "audit/governance_anchor.log"

def get_latest_chain_head(db: Session):
    last_event= db.query(GovernanceEventLog)\
    .order_by(GovernanceEventLog.created_at.desc())\
    .first()

    return last_event.event_hash if last_event else None


def get_last_anchored_hash(db: Session):
    last_anchor = db.query(GovernanceAnchor)\
        .order_by(GovernanceAnchor.anchored_at.desc())\
        .first()

    return last_anchor.anchored_hash if last_anchor else None

def anchor_chain_head(db: Session, source: str = "scheduler"):

    head_hash = get_latest_chain_head(db)
    if not head_hash:
        return None

    last_anchored = get_last_anchored_hash(db)

    # 🔐 Do nothing if no change
    if head_hash == last_anchored:
        return None

    anchor = GovernanceAnchor(
        anchored_hash=head_hash,
        anchor_source=source,
        anchored_at=datetime.utcnow()
    )

    db.add(anchor)
    # Commit is handled at a higher level.
    db.flush()

    os.makedirs("audit", exist_ok=True)

    with open(ANCHOR_FILE_PATH, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} | {head_hash}\n")

    return head_hash

