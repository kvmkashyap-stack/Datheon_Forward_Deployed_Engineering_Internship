
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_metrics_endpoint_exposes_prometheus_format():
    client.get("/health/live")

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "ai_service_requests_total" in response.text
    assert "ai_service_request_duration_seconds" in response.text


def test_metrics_endpoint_uses_prometheus_content_type():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
