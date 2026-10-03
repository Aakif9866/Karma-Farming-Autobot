import pytest
from fastapi.testclient import TestClient


def test_liveness_needs_no_dependencies() -> None:
    from app.main import create_app

    r = TestClient(create_app()).get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.integration
def test_readiness_ok(client: TestClient) -> None:
    r = client.get("/api/v1/health/ready")
    assert r.status_code == 200, r.text
    assert r.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}
