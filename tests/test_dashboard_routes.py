from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import dashboard as dashboard_api


def _fake_db():
    yield object()


def test_dashboard_summary_route_returns_summary(monkeypatch):
    app = FastAPI()
    app.include_router(dashboard_api.router)
    app.dependency_overrides[dashboard_api.get_db] = _fake_db

    monkeypatch.setattr(
        dashboard_api,
        "get_dashboard_summary",
        lambda _db, tenant_id: {
            "tenant_id": tenant_id,
            "total_controls": 2,
            "audit_readiness": 0.85,
            "average_risk": 0.15,
            "distribution": {"high": 0, "medium": 1, "low": 1},
            "top_risks": [
                {
                    "control_id": "CTRL-1",
                    "risk_score": 0.22,
                    "risk_level": "MEDIUM",
                }
            ],
            "last_updated": "2026-04-07T12:21:56",
        },
    )

    client = TestClient(app)
    response = client.get("/dashboard/summary", params={"tenant_id": "demo"})

    assert response.status_code == 200
    assert response.json()["tenant_id"] == "demo"


def test_dashboard_controls_route_returns_controls(monkeypatch):
    app = FastAPI()
    app.include_router(dashboard_api.router)
    app.dependency_overrides[dashboard_api.get_db] = _fake_db

    monkeypatch.setattr(
        dashboard_api,
        "get_controls_for_tenant",
        lambda _db, tenant_id: [
            {
                "control_id": "CTRL-1",
                "failure_probability": 0.22,
                "risk_level": "MEDIUM",
                "updated_at": "2026-04-07T12:21:56",
            }
        ]
        if tenant_id == "demo"
        else [],
    )

    client = TestClient(app)
    response = client.get("/dashboard/controls", params={"tenant_id": "demo"})

    assert response.status_code == 200
    assert response.json()[0]["control_id"] == "CTRL-1"
