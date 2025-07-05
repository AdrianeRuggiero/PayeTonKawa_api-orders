import pytest
from datetime import datetime
from app.messaging.schemas import (
    OrderProductMessage,
    OrderMessage,
    OrderDeletedMessage
)

#  Teste un produit valide
def test_order_product_message_valid():
    msg = OrderProductMessage(product_id="p1", quantity=2)
    assert msg.product_id == "p1"
    assert msg.quantity == 2

#  Teste une erreur si la quantité est <= 0
def test_order_product_message_invalid_quantity():
    with pytest.raises(ValueError):
        OrderProductMessage(product_id="p2", quantity=0)

#  Teste un message complet valide
def test_order_message_valid():
    msg = OrderMessage(
        id="order001",
        client_id="client123",
        products=[{"product_id": "p1", "quantity": 1}],
        total_price=59.99,
        status="shipped",
        created_at=datetime.utcnow()
    )
    assert msg.id == "order001"
    assert msg.total_price > 0

#  Teste une erreur si total_price <= 0
def test_order_message_invalid_price():
    with pytest.raises(ValueError):
        OrderMessage(
            id="order002",
            client_id="client456",
            products=[{"product_id": "p2", "quantity": 1}],
            total_price=0.0,
            status="cancelled",
            created_at=datetime.utcnow()
        )

#  Teste un message de commande supprimée
def test_order_deleted_message_valid():
    msg = OrderDeletedMessage(order_id="order003")
    assert msg.order_id == "order003"
