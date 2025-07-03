from pymongo import MongoClient
from app.config import settings  # Contient MONGO_URI et DATABASE_NAME

# ────────────────────────────────
# Connexion à la base MongoDB
# ────────────────────────────────

# Crée un client MongoDB à partir de l'URI définie dans le fichier .env
client = MongoClient(settings.MONGO_URI)

# Sélectionne la base de données (ex: "orders_db")
db = client[settings.DATABASE_NAME]

# Accès à la collection "orders" dans la base
orders_collection = db["orders"]
