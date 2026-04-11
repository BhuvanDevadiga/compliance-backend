from datetime import datetime
from unittest.mock import MagicMock

from app.models.control import Control
from app.services.dashboard_service import get_controls_for_tenant


def test_get_controls_for_tenant_serializes_control_model_fields():
    db = MagicMock()
    control = Control(
        id="ctrl-1",
        tenant_id="demo",
        name="Access Review",
        framework="SOC2",
        control_failure_prob=0.42,
        control_risk_level="MEDIUM",
        control_risk_updated_at=datetime(2026, 4, 7, 12, 21, 56),
    )

    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [control]

    result = get_controls_for_tenant(db, "demo")

    assert result == [
        {
            "control_id": "ctrl-1",
            "failure_probability": 0.42,
            "risk_level": "MEDIUM",
            "updated_at": "2026-04-07T12:21:56",
        }
    ]
