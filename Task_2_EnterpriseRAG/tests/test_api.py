
from fastapi.testclient import TestClient

from enterprise_rag.api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["app_name"] == "EnterpriseRAG"


def test_unknown_user_is_rejected() -> None:
    response = client.post(
        "/query",
        json={
            "user_id": "unknown-user",
            "question": "What are the termination conditions?",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Unknown demo user ID."


def test_empty_question_is_rejected() -> None:
    response = client.post(
        "/query",
        json={
            "user_id": "demo-internal",
            "question": "",
        },
    )

    assert response.status_code == 422
