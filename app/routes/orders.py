from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.order import OrderCreate, OrderDB, OrderUpdate
from app.services.order_service import OrderService
from app.db.mongo import orders_collection
from app.security.dependencies import require_admin, get_current_user



router = APIRouter(prefix="/orders", tags=["Orders"])
order_service = OrderService(orders_collection)

# ───────────────────────────────────────────────────────────────
# POST /orders : Créer une commande
# Accessible à tous les utilisateurs authentifiés (user + admin)
# ───────────────────────────────────────────────────────────────
@router.post("/", response_model=OrderDB, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, user: dict = Depends(get_current_user)):
    # Forcer l’ID du client à celui de l’utilisateur connecté
    order.client_id = user["sub"]  # supposé être l'id unique de l'utilisateur
    return order_service.create_order(order)

# ───────────────────────────────────────────────────────────────
# GET /orders : Récupérer toutes les commandes
# Admin → toutes, User → seulement les siennes
# ───────────────────────────────────────────────────────────────
@router.get("/", response_model=List[OrderDB])
def get_all_orders(user: dict = Depends(get_current_user)):
    if user["role"] == "admin":
        return order_service.get_all_orders()
    else:
        return order_service.get_orders_by_client_id(user["sub"])

# ───────────────────────────────────────────────────────────────
# GET /orders/{order_id} : Récupérer une commande spécifique
# Admin → toutes, User → seulement ses propres commandes
# ───────────────────────────────────────────────────────────────
@router.get("/{order_id}", response_model=OrderDB)
def get_order(order_id: str, user: dict = Depends(get_current_user)):
    order = order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    if user["role"] != "admin" and order.client_id != user["sub"]:
        raise HTTPException(status_code=403, detail="Accès interdit")
    return order

# ───────────────────────────────────────────────────────────────
# PUT /orders : Modifier une commande
# Admin → toutes, User → seulement ses propres commandes
# ───────────────────────────────────────────────────────────────

@router.put("/{order_id}", response_model=OrderDB)
def update_order(order_id: str, updates: OrderUpdate, user: dict = Depends(get_current_user)):
    existing_order = order_service.get_order(order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")

    if user["role"] != "admin":
        if existing_order.client_id != user["sub"]:
            raise HTTPException(status_code=403, detail="Accès interdit à cette commande")
        if existing_order.status != "pending":
            raise HTTPException(status_code=403, detail="Seules les commandes 'pending' sont modifiables")

    update_data = updates.dict(exclude_unset=True)
    updated_order = order_service.update_order(order_id, update_data)
    if not updated_order:
        raise HTTPException(status_code=400, detail="Échec de la mise à jour")
    return updated_order

# ───────────────────────────────────────────────────────────────
# DELETE /orders/{order_id} : Supprimer une commande
# Admin uniquement
# ───────────────────────────────────────────────────────────────
@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: str, user: dict = Depends(require_admin)):
    success = order_service.delete_order(order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
