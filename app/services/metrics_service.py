from sqlalchemy.orm import Session
from app.models.tenant_system_state import TenantSystemState
from app.models.system_state import GlobalSystemState
from app.services.health_service import compute_regret_risk_index
from app.core.engine_config import ENGINE_VERSION

def build_prometheus_metrics(db: Session) -> str:

    lines = []

    global_state = db.query(GlobalSystemState).first()
    if not global_state:
        global_state = GlobalSystemState(id="GLOBAL")
        db.add(global_state)
        db.commit()
        db.refresh(global_state)
    tenants = db.query(TenantSystemState).all()

    # Platform override metric
    override_value = 1 if global_state and global_state.platform_override_active else 0
    lines.append("# HELP platform_override_active Platform emergency override status")
    lines.append("# TYPE platform_override_active gauge")
    lines.append(f'platform_override_active{{engine_version="{ENGINE_VERSION}"}} {override_value}')

    # Tenant counts
    total_tenants = len(tenants)
    frozen_count = sum(1 for t in tenants if t.adaptive_engine_frozen)

    lines.append("# HELP total_tenants Total registered tenants")
    lines.append("# TYPE total_tenants gauge")
    lines.append(f"total_tenants {total_tenants}")

    lines.append("# HELP frozen_tenants Number of frozen tenants")
    lines.append("# TYPE frozen_tenants gauge")
    lines.append(f"frozen_tenants {frozen_count}")

    # Per-tenant metrics
    lines.append("# HELP tenant_regret_risk_index Regret Risk Index per tenant")
    lines.append("# TYPE tenant_regret_risk_index gauge")

    lines.append("# HELP tenant_frozen_status Tenant freeze status")
    lines.append("# TYPE tenant_frozen_status gauge")

    for tenant in tenants:

        health = compute_regret_risk_index(db, tenant.tenant_id)

        rri = health["regret_risk_index"]
        frozen = 1 if tenant.adaptive_engine_frozen else 0

        lines.append(
            f'tenant_regret_risk_index{{tenant_id="{tenant.tenant_id}"}} {rri}'
        )

        lines.append(
            f'tenant_frozen_status{{tenant_id="{tenant.tenant_id}"}} {frozen}'
        )

    return "\n".join(lines)

