import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_forecast_returns_requested_horizon():
    resp = client.get("/api/forecast", params={"horizon_days": 7})
    assert resp.status_code == 200
    body = resp.json()
    assert body["horizon_days"] == 7
    assert len(body["points"]) == 7
    assert all(p["forecast"] >= 0 for p in body["points"])


def test_staffing_plan_produces_a_schedule():
    resp = client.get("/api/staffing-plan", params={"horizon_days": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] in ("optimal", "TerminationCondition.optimal")
    assert body["total_cost"] > 0
    assert len(body["schedule"]) > 0
