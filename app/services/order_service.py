from typing import List, Optional
from pymongo.collection import Collection
from app.models.order import OrderCreate, OrderDB
from bson import ObjectId
from app.messaging.rabbitmq import publish_order_created


class OrderService:
    # Initialise le service avec la collection MongoDB 'orders'
    def __init__(self, orders_collection: Collection):
        self.collection = orders_collection

    # Crée une commande à partir des données reçues
    def create_order(self, order: OrderCreate) -> OrderDB:
        order_dict = order.model_dump()
        # Créer une instance OrderDB avec id auto-généré
        new_order = OrderDB(**order_dict)  # Génère un ID et une date
        self.collection.insert_one(new_order.model_dump())  # Sauvegarde dans Mongo
        # Préparer les données pour RabbitMQ (avec created_at au format ISO)
        serialized = new_order.model_dump()
        serialized["created_at"] = new_order.created_at.isoformat()
        publish_order_created(serialized)       # Envoie un message RabbitMQ
        return new_order

    # Récupère une commande par son ID
    def get_order(self, order_id: str) -> Optional[OrderDB]:
        data = self.collection.find_one({"id": order_id})
        if data:
            return OrderDB(**data)
        return None

    # Récupère toutes les commandes
    def get_all_orders(self) -> List[OrderDB]:
        orders = self.collection.find()
        return [OrderDB(**order) for order in orders]

    # Supprime une commande par ID
    def delete_order(self, order_id: str) -> bool:
        result = self.collection.delete_one({"id": order_id})
        return result.deleted_count == 1
