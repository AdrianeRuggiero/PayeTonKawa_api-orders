import pytest
from app.models.order import (
    OrderProduct,
    OrderCreate,
    OrderUpdate,
    OrderDB,
)
from datetime import datetime
from uuid import UUID

# Test de OrderProduct

def test_order_product_valid():
    prod = OrderProduct(product_id="prod001", quantity=2)
    assert prod.product_id == "prod001"
    assert prod.quantity == 2

def test_order_product_invalid_quantity():
    with pytest.raises(ValueError):
        OrderProduct(product_id="prod001", quantity=0)  # Doit échouer (gt=0)

# Test de OrderCreate

def test_order_create_valid():
    data = OrderCreate(
        client_id="client123",
        products=[OrderProduct(product_id="p1", quantity=1)],
        total_price=49.99,
    )
    assert data.client_id == "client123"
    assert data.total_price == 49.99
    assert data.status == "pending"
    assert isinstance(data.created_at, datetime)

def test_order_create_missing_total_price():
    with pytest.raises(ValueError):
        OrderCreate(
            client_id="client123",
            products=[OrderProduct(product_id="p1", quantity=1)],
        )

# Test de OrderDB

def test_order_db_defaults():
    order = OrderDB(
        client_id="client999",
        products=[OrderProduct(product_id="prodX", quantity=5)],
        total_price=120.0
    )
    assert isinstance(UUID(order.id), UUID)
    assert order.client_id == "client999"
    assert order.status == "pending"
    assert isinstance(order.created_at, datetime)

# Test de OrderUpdate

def test_order_update_partial():
    update = OrderUpdate(
        products=[OrderProduct(product_id="prodY", quantity=2)],
        total_price=99.99,
        status="confirmed"
    )
    assert update.status == "confirmed"
    assert update.total_price == 99.99
    assert len(update.products) == 1

def test_order_update_empty():
    update = OrderUpdate()
    assert update.products is None
    assert update.total_price is None
    assert update.status is None
