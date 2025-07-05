import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.models.order import OrderDB
from app.security.dependencies import get_current_user, require_admin

client = TestClient(app)

# Utilisateurs simulés
USER = {"sub": "user1", "role": "user"}
ADMIN = {"sub": "admin", "role": "admin"}

# Appliquer pour chaque test
def setup_function():
    app.dependency_overrides[get_current_user] = lambda: USER
    app.dependency_overrides[require_admin] = lambda: ADMIN

# POST /orders

@patch("app.routes.orders.order_service.create_order")
def test_create_order(mock_create):
    payload = {
        "products": [{"product_id": "p1", "quantity": 2}],
        "total_price": 49.99
    }
    mock_create.return_value = {
        "id": "order1",
        "client_id": USER["sub"],
        "products": payload["products"],
        "total_price": 49.99,
        "status": "pending",
        "created_at": "2024-07-01T12:00:00"
    }
    response = client.post("/orders/", json=payload)
    assert response.status_code == 201

# GET /orders

@patch("app.routes.orders.order_service.get_orders_by_client_id")
def test_get_orders_user(mock_get):
    mock_get.return_value = []
    response = client.get("/orders/")
    assert response.status_code == 200

@patch("app.routes.orders.order_service.get_all_orders")
def test_get_orders_admin(mock_get):
    app.dependency_overrides[get_current_user] = lambda: ADMIN
    mock_get.return_value = []
    response = client.get("/orders/")
    assert response.status_code == 200

# GET /orders/{id}

@patch("app.routes.orders.order_service.get_order")
def test_get_order_not_found(mock_get):
    mock_get.return_value = None
    response = client.get("/orders/x")
    assert response.status_code == 404

@patch("app.routes.orders.order_service.get_order")
def test_get_order_forbidden(mock_get):
    mock_get.return_value = OrderDB(
        id="x", client_id="other", products=[],
        total_price=10, status="pending", created_at="2024-07-01T12:00:00"
    )
    response = client.get("/orders/x")
    assert response.status_code == 403

@patch("app.routes.orders.order_service.get_order")
def test_get_order_ok(mock_get):
    mock_get.return_value = OrderDB(
        id="x", client_id=USER["sub"], products=[],
        total_price=10, status="pending", created_at="2024-07-01T12:00:00"
    )
    response = client.get("/orders/x")
    assert response.status_code == 200

# PUT /orders/{id}

@patch("app.routes.orders.order_service.get_order")
def test_update_not_found(mock_get):
    mock_get.return_value = None
    response = client.put("/orders/1", json={"total_price": 99.9})
    assert response.status_code == 404

@patch("app.routes.orders.order_service.get_order")
def test_update_forbidden_user(mock_get):
    mock_get.return_value = OrderDB(
        id="1", client_id="not_user1", products=[],
        total_price=10, status="pending", created_at="2024-07-01T12:00:00"
    )
    response = client.put("/orders/1", json={"total_price": 99.9})
    assert response.status_code == 403

@patch("app.routes.orders.order_service.get_order")
def test_update_forbidden_status(mock_get):
    mock_get.return_value = OrderDB(
        id="1", client_id=USER["sub"], products=[],
        total_price=10, status="shipped", created_at="2024-07-01T12:00:00"
    )
    response = client.put("/orders/1", json={"total_price": 99.9})
    assert response.status_code == 403

@patch("app.routes.orders.order_service.update_order")
@patch("app.routes.orders.order_service.get_order")
def test_update_success(mock_get, mock_update):
    mock_get.return_value = OrderDB(
        id="1", client_id=USER["sub"], products=[],
        total_price=10, status="pending", created_at="2024-07-01T12:00:00"
    )
    mock_update.return_value = {
        "id": "1", "client_id": USER["sub"], "products": [],
        "total_price": 99.9, "status": "pending", "created_at": "2024-07-01T12:00:00"
    }
    response = client.put("/orders/1", json={"total_price": 99.9})
    assert response.status_code == 200

@patch("app.routes.orders.order_service.update_order")
@patch("app.routes.orders.order_service.get_order")
def test_update_failed(mock_get, mock_update):
    mock_get.return_value = OrderDB(
        id="1", client_id=USER["sub"], products=[],
        total_price=10, status="pending", created_at="2024-07-01T12:00:00"
    )
    mock_update.return_value = None
    response = client.put("/orders/1", json={"total_price": 99.9})
    assert response.status_code == 400

# DELETE /orders/{id}

@patch("app.routes.orders.order_service.delete_order")
def test_delete_success(mock_delete):
    mock_delete.return_value = True
    response = client.delete("/orders/1")
    assert response.status_code == 204

@patch("app.routes.orders.order_service.delete_order")
def test_delete_not_found(mock_delete):
    mock_delete.return_value = False
    response = client.delete("/orders/404")
    assert response.status_code == 404
