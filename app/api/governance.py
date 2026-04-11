from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.governance_controller import compute_governance_adjustments
from typing import Optional
from app.models.governance_event_log import GovernanceEventLog
from sqlalchemy import func
from app.models.system_state import GlobalSystemState
from app.services.tenant_state_service import get_tenant_state
from app.core.engine_config import ENGINE_VERSION  
from app.services.health_service import compute_regret_risk_index 
from app.services.dashboard_service import build_governance_dashboard
from fastapi.responses import PlainTextResponse
from app.services.metrics_service import build_prometheus_metrics
from app.services.signing_service import verify_signature, compute_event_hash
from app.services.anchor_service import anchor_chain_head
from app.services.compliance_export_service import generate_compliance_bundle
from app.services.instability_model import compute_instability_probability, get_instability_features
from datetime import datetime
from app.services.risk_metrics_service import get_regret_risk_index
from app.services.governance_dashboard_service import get_governance_overview
from app.services.governance_integrity import verify_tenant_chain


router = APIRouter(prefix="/api/tenant", tags=["governance"])
metrics_router = APIRouter(prefix="/api/governance", tags=["governance"])

@router.get("/governance/{tenant_id}")
def tenant_governance(tenant_id: str, db: Session = Depends(get_db)):
    return compute_governance_adjustments(db, tenant_id)


@router.get("/events")
def get_governance_events(
    tenant_id: Optional[str] = Query(None, description="Tenant identifier"),
    event_type: Optional[str] = Query(None, description="FREEZE or UNLOCK"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(GovernanceEventLog)

    if tenant_id:
        query = query.filter(GovernanceEventLog.tenant_id == tenant_id)

    if event_type:
        query = query.filter(GovernanceEventLog.event_type == event_type)

    events = (
        query.order_by(GovernanceEventLog.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        {
            "id": e.id,
            "tenant_id": e.tenant_id,
            "event_type": e.event_type,
            "previous_version": e.previous_version,
            "new_version": e.new_version,
            "reason": e.reason,
            "created_at": e.created_at,
        }
        for e in events
    ]

@router.get("/metrics")
def get_governance_metrics(
    tenant_id: Optional[str] = Query(None, description="Tenant identifier"),
    db: Session = Depends(get_db),
):

    # Count events
    event_query = db.query(GovernanceEventLog)
    if tenant_id:
        event_query = event_query.filter(GovernanceEventLog.tenant_id == tenant_id)

    total_freezes = (
        event_query.filter(GovernanceEventLog.event_type == "FREEZE")
        .count()
    )

    total_unlocks = (
        event_query.filter(GovernanceEventLog.event_type == "UNLOCK")
        .count()
    )

    # Last freeze
    last_freeze_query = (
        db.query(GovernanceEventLog)
        .filter(GovernanceEventLog.event_type == "FREEZE")
    )
    if tenant_id:
        last_freeze_query = last_freeze_query.filter(
            GovernanceEventLog.tenant_id == tenant_id
        )
    last_freeze = last_freeze_query.order_by(
        GovernanceEventLog.created_at.desc()
    ).first()

    # Last unlock
    last_unlock_query = (
        db.query(GovernanceEventLog)
        .filter(GovernanceEventLog.event_type == "UNLOCK")
    )
    if tenant_id:
        last_unlock_query = last_unlock_query.filter(
            GovernanceEventLog.tenant_id == tenant_id
        )
    last_unlock = last_unlock_query.order_by(
        GovernanceEventLog.created_at.desc()
    ).first()

    # Current state
    if tenant_id:
        state = get_tenant_state(db, tenant_id)
    else:
        state = db.query(GlobalSystemState).first()

    return {
        "current_engine_version": ENGINE_VERSION,
        "adaptive_engine_frozen": state.adaptive_engine_frozen if state else None,
        "freeze_locked_version": state.freeze_locked_version if state else None,
        "total_freezes": total_freezes,
        "total_unlocks": total_unlocks,
        "last_freeze_at": last_freeze.created_at if last_freeze else None,
        "last_unlock_at": last_unlock.created_at if last_unlock else None,
    }

@router.get("/health")
def get_governance_health(tenant_id : str, db: Session = Depends(get_db)):
   
    return compute_regret_risk_index(db, tenant_id)

@router.get("/dashboard")
def get_governance_dashboard(db: Session = Depends(get_db)):
    return build_governance_dashboard(db)

@metrics_router.get(
    "/metrics",
    response_class=PlainTextResponse,
    responses={200: {"content": {"text/plain; version=0.0.4": {}}}},
)
def get_prometheus_metrics(db: Session = Depends(get_db)):
    return build_prometheus_metrics(db)

@router.get("/verify-integrity")
def verify_governance_integrity(db: Session = Depends(get_db)):

    events = db.query(GovernanceEventLog)\
        .order_by(GovernanceEventLog.created_at.asc())\
        .all()

    previous_hash = None
    legacy_phase = True
    legacy_unsigned_count = 0
    verified_signed_count = 0

    for event in events:
        
        payload = event.original_payload or f"{event.event_type}|{event.tenant_id}|{event.reason}|{event.created_at}"
        expected_hash = compute_event_hash(payload, previous_hash)

        # 🔐 Always verify hash chain integrity
        if event.event_hash != expected_hash:
            return {
                "status": "CORRUPTED",
                "event_id": event.id
            }

        # 🟡 Handle legacy unsigned events (allowed only at beginning)
        if not event.signing_key_id or not event.signature:

            if not legacy_phase:
                return {
                    "status": "FAILED",
                    "reason": "Unsigned event found after signing phase began",
                    "event_id": event.id
                }

            legacy_unsigned_count += 1
            previous_hash = event.event_hash
            continue

        # 🔵 Signed phase begins
        legacy_phase = False

        if not verify_signature(db, event.event_hash, event.signature, event.signing_key_id):
            return {
                "status": "SIGNATURE_INVALID",
                "event_id": event.id
            }

        verified_signed_count += 1
        previous_hash = event.event_hash

    return {
        "status": "OK",
        "verified_signed_events": verified_signed_count,
        "legacy_unsigned_events": legacy_unsigned_count,
        "total_events": len(events)
    }

@router.post("/anchor")
def anchor_governance_chain(db: Session = Depends(get_db)):
    with db.begin():
        head_hash = anchor_chain_head(db)
    return {
        "status": "ANCHOR_CREATED",
        "anchored_hash": head_hash
    }

@router.get("/compliance-export")
def compliance_export(db: Session = Depends(get_db)):
    bundle = generate_compliance_bundle(db)
    return bundle

@router.get("/instability-score")
def get_instability_score(db:Session= Depends(get_db)):
    metrics = get_regret_risk_index(db)
    features = get_instability_features(metrics)
    probability = compute_instability_probability(**features)

    return{
        "instability_probability": probability,
        "features": features,
        "evaluated_at": datetime.utcnow()
    }

@router.get("/overview")
def governance_overview(db: Session = Depends(get_db)):
    return get_governance_overview(db)

@router.get("/integrity/{tenant_id}")
def verify_integrity(tenant_id: str, db: Session = Depends(get_db)):
    return {
        "tenant_id": tenant_id,
        "valid": verify_tenant_chain(db, tenant_id)
    }
                  
