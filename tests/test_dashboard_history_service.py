from datetime import datetime
from unittest.mock import MagicMock

from app.models.risk_history import RiskHistory
from app.services.dashboard_service import get_tenant_risk_history


def test_get_tenant_risk_history_uses_risk_history_model():
    db = MagicMock()
    snapshot = RiskHistory(
        tenant_id="demo",
        probability=0.42,
        created_at=datetime(2026, 4, 7, 15, 45, 0),
    )

    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [snapshot]

    result = get_tenant_risk_history(db, "demo")

    assert result == [
        {
            "risk_score": 0.42,
            "created_at": "2026-04-07T15:45:00",
        }
    ]
