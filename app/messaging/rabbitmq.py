import pika
import json
from app.config import settings
from app.messaging.schemas import OrderMessage, OrderDeletedMessage

# Connexion à RabbitMQ

def get_channel():
    """Crée une connexion et retourne (connection, channel) avec déclaration de 'order_created'."""
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="order_created", durable=True)
    return connection, channel

# Publisher : commande créée

def publish_order_created(order_data: dict, channel=None):
    validated = OrderMessage(**order_data)
    if channel is None:
        connection, channel = get_channel()
        close_connection = True
    else:
        close_connection = False

    channel.basic_publish(
        exchange="",
        routing_key="order_created",
        body=validated.model_dump_json(),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    if close_connection:
        connection.close()

# Publisher : commande modifiée

def publish_order_updated(order_data: dict, channel=None):
    validated = OrderMessage(**order_data)
    if channel is None:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue="order_updated", durable=True)
        close_connection = True
    else:
        close_connection = False

    channel.basic_publish(
        exchange="",
        routing_key="order_updated",
        body=validated.model_dump_json(),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    if close_connection:
        connection.close()        