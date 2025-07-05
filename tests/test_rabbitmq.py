import pytest
import json
from unittest.mock import patch, MagicMock
from app.messaging import rabbitmq


# UTILITY : Fake order data

order_data = {
    "id": "o1",
    "client_id": "c1",
    "products": [{"product_id": "p1", "quantity": 1}],
    "total_price": 59.99,
    "status": "pending",
    "created_at": "2024-07-05T10:00:00"
}

# TESTS : Publishers avec channel fourni

def test_publish_order_created_with_channel():
    channel = MagicMock()
    rabbitmq.publish_order_created(order_data, channel=channel)
    assert channel.basic_publish.called


def test_publish_order_updated_with_channel():
    channel = MagicMock()
    rabbitmq.publish_order_updated(order_data, channel=channel)
    assert channel.basic_publish.called


def test_publish_order_deleted_with_channel():
    channel = MagicMock()
    rabbitmq.publish_order_deleted("o1", channel=channel)
    assert channel.basic_publish.called


# TESTS : Publishers sans channel (mock connection)

@patch("app.messaging.rabbitmq.get_channel")
def test_publish_order_created_no_channel(mock_get_channel):
    mock_conn = MagicMock()
    mock_chan = MagicMock()
    mock_get_channel.return_value = (mock_conn, mock_chan)

    rabbitmq.publish_order_created(order_data)
    assert mock_chan.basic_publish.called
    mock_conn.close.assert_called_once()


@patch("app.messaging.rabbitmq.pika.BlockingConnection")
def test_publish_order_updated_no_channel(mock_connection_class):
    mock_conn = MagicMock()
    mock_chan = MagicMock()
    mock_conn.channel.return_value = mock_chan
    mock_connection_class.return_value = mock_conn

    rabbitmq.publish_order_updated(order_data)
    mock_chan.basic_publish.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("app.messaging.rabbitmq.pika.BlockingConnection")
def test_publish_order_deleted_no_channel(mock_connection_class):
    mock_conn = MagicMock()
    mock_chan = MagicMock()
    mock_conn.channel.return_value = mock_chan
    mock_connection_class.return_value = mock_conn

    rabbitmq.publish_order_deleted("order123")
    mock_chan.basic_publish.assert_called_once()
    mock_conn.close.assert_called_once()


# TEST : get_channel()

@patch("app.messaging.rabbitmq.pika.BlockingConnection")
def test_get_channel(mock_connection_class):
    mock_conn = MagicMock()
    mock_chan = MagicMock()
    mock_conn.channel.return_value = mock_chan
    mock_connection_class.return_value = mock_conn

    conn, chan = rabbitmq.get_channel()
    chan.queue_declare.assert_called_with(queue="order_created", durable=True)
    assert conn == mock_conn
    assert chan == mock_chan


# TESTS : Consumers (wrapper)

def simulate_message(callback, body_dict):
    body = json.dumps(body_dict).encode()
    mock_ch = MagicMock()
    mock_method = MagicMock()
    mock_method.delivery_tag = "123"
    callback(mock_ch, mock_method, None, body)
    return mock_ch, mock_method


@pytest.mark.parametrize("consume_func, queue", [
    (rabbitmq.consume_product_created, "product_created"),
    (rabbitmq.consume_product_updated, "product_updated"),
    (rabbitmq.consume_product_deleted, "product_deleted"),
    (rabbitmq.consume_client_created, "client_created"),
    (rabbitmq.consume_client_updated, "client_updated"),
    (rabbitmq.consume_client_deleted, "client_deleted"),
])
def test_consumers_trigger_callback(consume_func, queue):
    callback = MagicMock()

    with patch("app.messaging.rabbitmq.pika.BlockingConnection") as mock_conn_class:
        mock_conn = MagicMock()
        mock_chan = MagicMock()
        mock_conn.channel.return_value = mock_chan
        mock_conn_class.return_value = mock_conn

        def fake_basic_consume(queue, on_message_callback, *args, **kwargs):
            assert queue  # utile juste pour forcer l’appel
            mock_ch, mock_method = simulate_message(on_message_callback, {"test": True})
            mock_ch.basic_ack.assert_called_with(delivery_tag="123")

        mock_chan.basic_consume.side_effect = fake_basic_consume
        mock_chan.start_consuming = MagicMock()

        consume_func(callback)
        callback.assert_called_with({"test": True})
