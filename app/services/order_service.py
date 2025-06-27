from typing import List, Optional
from pymongo.collection import Collection
from app.models.order import OrderCreate, OrderDB
from bson import ObjectId
from app.messaging.rabbitmq import publish_order_created

# Classe de service pour gérer les opérations CRUD liées aux commandes (orders)
class OrderService:
    def __init__(self, orders_collection: Collection):
        # Initialisation avec la collection MongoDB
        self.collection = orders_collection

    # Création d'une nouvelle commande
    def create_order(self, order: OrderCreate) -> OrderDB:
        # Conversion de l'objet Pydantic en dictionnaire
        order_dict = order.dict()
        # Création d'un objet OrderDB (avec ID, etc.)
        new_order = OrderDB(**order_dict)
        # Insertion de la commande dans MongoDB
        self.collection.insert_one(new_order.dict())
        # Publication d'un message dans RabbitMQ pour notifier la création
        publish_order_created(new_order.dict())
        # Retourne la commande créée
        return new_order

    # Récupération d'une commande par son identifiant
    def get_order(self, order_id: str) -> Optional[OrderDB]:
        # Recherche dans MongoDB par ID
        data = self.collection.find_one({"id": order_id})
        # Si une commande est trouvée, on la retourne sous forme d'objet OrderDB
        if data:
            return OrderDB(**data)
        return None  # Sinon, on retourne None

    # Récupération de toutes les commandes
    def get_all_orders(self) -> List[OrderDB]:
        # Recherche de tous les documents dans la collection
        orders = self.collection.find()
        # Transformation de chaque document en objet OrderDB
        return [OrderDB(**order) for order in orders]

    # Suppression d'une commande par son ID
    def delete_order(self, order_id: str) -> bool:
        # Suppression du document correspondant dans MongoDB
        result = self.collection.delete_one({"id": order_id})
        # Retourne True si un document a été supprimé, sinon False
        return result.deleted_count == 1
