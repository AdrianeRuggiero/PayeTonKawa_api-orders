from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

# Modèle pour représenter un produit dans une commande
class OrderProduct(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)  # Quantité minimale = 1

# Modèle de base commun pour la création et la réponse
class OrderBase(BaseModel):

    products: List[OrderProduct]
    total_price: float = Field(..., gt=0)
    status: str = "pending"  # Statuts possibles : pending, confirmed, shipped, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Modèle utilisé à la création (POST) — identique à OrderBase
class OrderCreate(OrderBase):
    client_id: Optional[str] = None

# Modèle utilisé pour les données stockées en base ou retournées à l’API
class OrderDB(OrderBase):
    id: str = Field(default_factory=lambda: str(uuid4()))  # UUID auto-généré pour chaque commande
    client_id: str #requis pour l'enregistrement en base 

    class Config:
        orm_mode = True  # Compatible avec les retours d’objets
        schema_extra = {
            "example": {
                 "id": "9b8fba46-14df-4f9b-b3c1-d99316d2eced",
                "client_id": "client123",
                "products": [
                    {"product_id": "prod001", "quantity": 2},
                    {"product_id": "prod002", "quantity": 1}
                ],
                "total_price": 59.99,
                "status": "pending",
                "created_at": "2024-06-28T12:00:00Z"
            }
        }

# Modèle utilisé pour la modification d'une commande
class OrderUpdate(BaseModel):
    products: Optional[List[OrderProduct]] = None
    total_price: Optional[float] = Field(None, gt=0)
    status: Optional[str] = None

    class Config:
        
        schema_extra = {
            "example": {
                "products": [
                    {"product_id": "prod001", "quantity": 3}
                ],
                "total_price": 79.99,
                "status": "confirmed"
            }
        }
