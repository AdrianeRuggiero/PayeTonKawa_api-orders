"""Main FastAPI application for the Orders microservice."""
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from app.routes import orders, token


# Création de l'application FastAPI avec métadonnées
app = FastAPI(
    title="Orders API",                      # Nom affiché dans Swagger
    version="1.0.0",                         # Version de l'API
    description="API de gestion des commandes avec monitoring Prometheus"
)

# Instrumentation Prometheus pour exposer les métriques
# Accessible sur /metrics
Instrumentator().instrument(app).expose(app)

# Ajout du routeur des commandes
app.include_router(orders.router)

# Route /token pour l’authentification JWT
app.include_router(token.router)
