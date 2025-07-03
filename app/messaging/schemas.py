from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

# Représente un produit dans un message de commande
class OrderProductMessage(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)

# Message complet pour une commande créée ou mise à jour
class OrderMessage(BaseModel):
    id: str
    client_id: str
    products: List[OrderProductMessage]
    total_price: float = Field(..., gt=0)
    status: str
    created_at: datetime

# Message simplifié pour une commande supprimée
class OrderDeletedMessage(BaseModel):
    order_id: str
