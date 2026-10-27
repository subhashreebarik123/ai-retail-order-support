from datetime import date
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def make_order(
    order_id="ORD1001",
    customer_name="Customer A",
    status="Shipped",
    expected_delivery=date(2026, 10, 29),
):
    """Create a mock order without connecting to MySQL."""
    order = Mock()
    order.order_id = order_id
    order.customer_name = customer_name
    order.status = status
    order.expected_delivery = expected_delivery
    return order


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("main.find_order")
def test_existing_order(mock_find_order):
    mock_find_order.return_value = make_order()

    response = client.get("/orders/ORD1001")

    assert response.status_code == 200
    assert response.json()["order_id"] == "ORD1001"
    assert response.json()["status"] == "Shipped"
    mock_find_order.assert_called_once_with("ORD1001")


@patch("main.find_order")
def test_unknown_order(mock_find_order):
    mock_find_order.return_value = None

    response = client.get("/orders/ORD9999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@patch("main.find_order")
def test_chat_existing_order(mock_find_order):
    mock_find_order.return_value = make_order()

    response = client.post(
        "/chat",
        json={"question": "Where is my order ORD1001?"},
    )

    assert response.status_code == 200
    assert "ORD1001" in response.json()["answer"]
    assert "Shipped" in response.json()["answer"]
    mock_find_order.assert_called_once_with("ORD1001")


@patch("main.find_order")
def test_chat_unknown_order(mock_find_order):
    mock_find_order.return_value = None

    response = client.post(
        "/chat",
        json={"question": "Where is my order ORD9999?"},
    )

    assert response.status_code == 200
    assert "could not find order" in response.json()["answer"].lower()


@patch("main.search_policies")
def test_general_chat_uses_gemini(mock_search_policies):
    mock_search_policies.return_value = [
        "Customers may request a refund according to the retailer's policy."
    ]

    mock_response = Mock()
    mock_response.text = (
        "You can request a refund according to the retailer's policy."
    )

    mock_client = Mock()
    mock_client.models.generate_content.return_value = mock_response

    with patch("main.client", mock_client):
        response = client.post(
            "/chat",
            json={"question": "How can I request a refund?"},
        )

    assert response.status_code == 200
    assert "refund" in response.json()["answer"].lower()
    mock_search_policies.assert_called_once()
    mock_client.models.generate_content.assert_called_once()


def test_chat_empty_question():
    response = client.post(
        "/chat",
        json={"question": "   "},
    )

    assert response.status_code == 422
    assert "cannot be empty" in response.json()["detail"].lower()


def test_chat_missing_question():
    response = client.post(
        "/chat",
        json={},
    )

    assert response.status_code == 422

