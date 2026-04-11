from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.engine_config import ENGINE_VERSION
from app.models.control import Control
from app.models.risk_history import RiskHistory
from app.models.system_state import GlobalSystemState
from app.models.tenant_system_state import TenantSystemState
from app.services.health_service import compute_regret_risk_index



def build_governance_dashboard(db: Session):
    global_state = db.query(GlobalSystemState).first()
    tenants = db.query(TenantSystemState).all()

    tenant_snapshot = []
    frozen_count = 0
    high_risk_count = 0

    for tenant in tenants:
        health = compute_regret_risk_index(db, tenant.tenant_id)

        if tenant.adaptive_engine_frozen:
            frozen_count += 1

        if health["risk_level"] == "HIGH":
            high_risk_count += 1

        tenant_snapshot.append(
            {
                "tenant_id": tenant.tenant_id,
                "frozen": tenant.adaptive_engine_frozen,
                "risk_level": health["risk_level"],
                "regret_risk_index": health["regret_risk_index"],
                "rolling_average_regret": health.get("rolling_average_regret"),
            }
        )

    return {
        "engine_version": ENGINE_VERSION,
        "platform_override_active": (
            global_state.platform_override_active if global_state else False
        ),
        "platform_override_reason": (
            global_state.platform_override_reason if global_state else None
        ),
        "total_tenants": len(tenants),
        "frozen_tenants": frozen_count,
        "high_risk_tenants": high_risk_count,
        "tenant_health": tenant_snapshot,
        "evaluated_at": datetime.now(UTC),
    }


def get_dashboard_summary(db: Session, tenant_id: str):
    controls = (
        db.query(Control)
        .filter(Control.tenant_id == tenant_id)
        .all()
    )

    if not controls:
        return None

    total = len(controls)
    avg_risk = sum(c.control_failure_prob for c in controls) / total
    readiness = 1 - avg_risk

    high = sum(1 for c in controls if c.control_risk_level == "HIGH")
    medium = sum(1 for c in controls if c.control_risk_level == "MEDIUM")
    low = sum(1 for c in controls if c.control_risk_level == "LOW")

    top_controls = sorted(
        controls,
        key=lambda c: c.control_failure_prob,
        reverse=True,
    )[:5]

    updated_at_values = [c.control_risk_updated_at for c in controls if c.control_risk_updated_at]
    last_updated = max(updated_at_values) if updated_at_values else None

    return {
        "tenant_id": tenant_id,
        "audit_readiness": round(readiness, 4),
        "average_risk": round(avg_risk, 4),
        "total_controls": total,
        "distribution": {
            "high": high,
            "medium": medium,
            "low": low,
        },
        "top_risks": [
            {
                "control_id": c.id,
                "risk_score": round(c.control_failure_prob, 4),
                "risk_level": c.control_risk_level,
            }
            for c in top_controls
        ],
        "last_updated": last_updated,
    }

def get_controls_for_tenant(db, tenant_id: str):
    from app.models.control import Control

    controls = (
        db.query(Control)
        .filter(Control.tenant_id == tenant_id)
        .order_by(Control.control_failure_prob.desc())
        .all()
    )

    result = []
    for c in controls:
        result.append({
            "control_id": c.id,
            "failure_probability": round(c.control_failure_prob or 0, 4),
            "risk_level": c.control_risk_level,
            "updated_at": c.control_risk_updated_at.isoformat() if c.control_risk_updated_at else None
        })

    return result

def get_tenant_risk_history(db, tenant_id: str):
    snapshots = (
        db.query(RiskHistory)
        .filter(RiskHistory.tenant_id == tenant_id)
        .order_by(RiskHistory.created_at.asc())
        .all()
    )

    return [
        {
            "risk_score": round(s.probability, 4),
            "created_at": s.created_at.isoformat()
        }
        for s in snapshots
    ]

def generate_dashboard_insights(db, tenant_id: str):
    

    
    controls = db.query(Control).filter(Control.tenant_id == tenant_id).all()
    total = len(controls)

    high = len([c for c in controls if c.control_risk_level == "HIGH"])
    medium = len([c for c in controls if c.control_risk_level == "MEDIUM"])
    low = len([c for c in controls if c.control_risk_level == "LOW"])

    avg_risk = sum(c.control_failure_prob or 0 for c in controls) / total if total else 0
    audit_readiness = 1 - avg_risk

    insights = []

    insights.append(f"Audit readiness is currently {audit_readiness*100:.2f}%.")

    if total > 0:
        high_pct = (high / total) * 100
        insights.append(f"{high_pct:.0f}% of controls are HIGH risk.")

    if high > 0:
        insights.append(f"Immediate attention required for {high} high-risk controls.")

    
    snapshots = (
        db.query(RiskHistory)
        .filter(RiskHistory.tenant_id == tenant_id)
        .order_by(RiskHistory.created_at.asc())
        .all()
    )

    if len(snapshots) >= 2:
        first = snapshots[0].probability
        last = snapshots[-1].probability

        if last > first:
            insights.append("Risk trend shows an upward trajectory over time.")
        elif last < first:
            insights.append("Risk trend shows improvement over time.")
        else:
            insights.append("Risk levels have remained stable over time.")

    return insights
