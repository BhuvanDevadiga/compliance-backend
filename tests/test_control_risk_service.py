from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import app.services.control_risk_service as control_risk_service
from app.models.control import Control


def test_score_all_controls_persists_scores(monkeypatch):
    now = datetime.now(UTC).replace(tzinfo=None)
    control = Control(
        id="ctrl-1",
        tenant_id="tenant-1",
        name="Access Review",
        framework="SOC2",
        last_evidence_updated_at=now - timedelta(days=45),
        owner_last_login=now - timedelta(days=20),
        historical_failure_rate=0.3,
        next_audit_date=now + timedelta(days=30),
    )
    db = MagicMock()

    monkeypatch.setattr(
        control_risk_service,
        "get_controls_for_tenant",
        lambda _db, _tenant_id: [control],
    )

    results = control_risk_service.score_all_controls(db, "tenant-1")

    assert len(results) == 1
    assert results[0]["control_id"] == "ctrl-1"
    assert 0.0 <= results[0]["failure_probability"] <= 1.0
    assert results[0]["risk_level"] in {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert control.control_failure_prob == results[0]["failure_probability"]
    assert control.control_risk_level == results[0]["risk_level"]
    assert control.control_risk_updated_at is not None
    db.flush.assert_called_once()


def test_score_all_controls_handles_missing_optional_dates(monkeypatch):
    control = Control(
        id="ctrl-2",
        tenant_id="tenant-2",
        name="Policy Acknowledgement",
        framework="ISO27001",
        historical_failure_rate=0.1,
    )
    db = MagicMock()

    monkeypatch.setattr(
        control_risk_service,
        "get_controls_for_tenant",
        lambda _db, _tenant_id: [control],
    )

    results = control_risk_service.score_all_controls(db, "tenant-2")

    assert len(results) == 1
    assert 0.0 <= control.control_failure_prob <= 1.0
    assert control.control_risk_updated_at is not None
    db.flush.assert_called_once()
