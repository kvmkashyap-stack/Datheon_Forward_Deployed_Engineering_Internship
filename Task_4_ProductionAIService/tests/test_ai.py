
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_returns_mock_response():
    response = client.post(
        "/api/v1/generate",
        json={"prompt": "Explain RAG briefly"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["provider"] == "mock"
    assert data["model"] == "mock"
    assert "Explain RAG briefly" in data["answer"]
    assert data["input_tokens"] == 0
    assert data["output_tokens"] == 0


def test_generate_rejects_empty_prompt():
    response = client.post(
        "/api/v1/generate",
        json={"prompt": ""},
    )

    assert response.status_code == 422


def test_generate_rejects_missing_prompt():
    response = client.post("/api/v1/generate", json={})

    assert response.status_code == 422
