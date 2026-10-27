from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_existing_order():
    response = client.get("/orders/ORD1001")

    assert response.status_code == 200
    assert response.json()["order_id"] == "ORD1001"
    assert response.json()["status"] == "Shipped"


def test_unknown_order():
    response = client.get("/orders/ORD9999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_chat_existing_order():
    response = client.post(
        "/chat",
        json={"question": "Where is my order ORD1001?"}
    )

    assert response.status_code == 200
    assert "ORD1001" in response.json()["answer"]
    assert "Shipped" in response.json()["answer"]


def test_chat_unknown_order():
    response = client.post(
        "/chat",
        json={"question": "Where is my order ORD9999?"}
    )

    assert response.status_code == 200
    assert "could not find order" in response.json()["answer"].lower()


@patch("main.client.models.generate_content")
def test_general_chat_uses_gemini(mock_generate):
    mock_response = Mock()
    mock_response.text = "You can request a refund according to the retailer's policy."
    mock_generate.return_value = mock_response

    response = client.post(
        "/chat",
        json={"question": "How can I request a refund?"}
    )

    assert response.status_code == 200
    assert "refund" in response.json()["answer"].lower()
    mock_generate.assert_called_once()


def test_chat_empty_question():
    response = client.post(
        "/chat",
        json={"question": "   "}
    )

    assert response.status_code == 422
    assert "cannot be empty" in response.json()["detail"].lower()


def test_chat_missing_question():
    response = client.post(
        "/chat",
        json={}
    )

    assert response.status_code == 422
