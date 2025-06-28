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

    # Publisher : commande supprimée

def publish_order_deleted(order_id: str, channel=None):
    validated = OrderDeletedMessage(order_id=order_id)
    if channel is None:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue="order_deleted", durable=True)
        close_connection = True
    else:
        close_connection = False

    channel.basic_publish(
        exchange="",
        routing_key="order_deleted",
        body=validated.model_dump_json(),
        properties=pika.BasicProperties(delivery_mode=2),
    )

    if close_connection:
        connection.close()  

# Consumers

# Consumer du publish_product_created

def consume_product_created(callback):
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="product_created", durable=True)

    def wrapper(ch, method, properties, body):
        data = json.loads(body)
        callback(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="product_created", on_message_callback=wrapper)
    print("[*] En attente de messages sur 'product_created'. CTRL+C pour arrêter.")
    channel.start_consuming()

# Consumer du publish_product_updated

def consume_product_updated(callback):
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="product_updated", durable=True)

    def wrapper(ch, method, properties, body):
        data = json.loads(body)
        callback(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="product_updated", on_message_callback=wrapper)
    print("[*] En attente de messages sur 'product_updated'. CTRL+C pour arrêter.")
    channel.start_consuming()

# Consumer de publish_product_deleted

def consume_product_deleted(callback):
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue="product_deleted", durable=True)

    def wrapper(ch, method, properties, body):
        data = json.loads(body)
        callback(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="product_deleted", on_message_callback=wrapper)
    print("[*] En attente de messages sur 'product_deleted'. CTRL+C pour arrêter.")
    channel.start_consuming()    