import pytest
from pymongo.errors import ConfigurationError, ServerSelectionTimeoutError
from app.db.mongo import orders_collection, db, client
from app.config import settings


#  Vérifie que les paramètres de connexion sont bien définis
def test_mongo_config_values():
    assert settings.MONGO_URI.startswith(("mongodb://", "mongodb+srv://"))
    assert settings.DATABASE_NAME != ""


#  Vérifie que le client Mongo est bien initialisé
def test_mongo_client_connection():
    # Récupère les noms de toutes les bases
    db_names = client.list_database_names()
    assert isinstance(db_names, list)


#  Vérifie que la base configurée est bien accessible
def test_mongo_database_access():
    # Vérifie que la base configurée contient bien une collection (même vide)
    collections = db.list_collection_names()
    assert isinstance(collections, list)


#  Vérifie que la collection "orders" est bien accessible
def test_orders_collection_exists():
    # Tu peux insérer puis supprimer un document test si nécessaire
    doc_id = orders_collection.insert_one({"test": True}).inserted_id
    found = orders_collection.find_one({"_id": doc_id})
    assert found is not None
    orders_collection.delete_one({"_id": doc_id})


# Vérifie le comportement si l’URI est invalide (test d’erreur)
def test_invalid_mongo_uri(monkeypatch):
    from pymongo import MongoClient

    # Change temporairement l’URI vers une adresse invalide
    monkeypatch.setenv("MONGO_URI", "mongodb://invalid:9999")

    # Crée un client avec l'URI invalide
    bad_client = MongoClient("mongodb://invalid:9999", serverSelectionTimeoutMS=1000)

    # Forcer une vraie tentative de connexion
    with pytest.raises(ServerSelectionTimeoutError):
        bad_client.server_info()  # <-- ici, Mongo tente de se connecter
