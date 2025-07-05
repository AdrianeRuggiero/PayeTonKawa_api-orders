from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Teste l’obtention d’un token pour un utilisateur
def test_token_user():
    response = client.post("/token", data={"username": "johndoe", "password": "secret"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


# Teste l’obtention d’un token pour un admin
def test_token_admin():
    response = client.post("/token", data={"username": "admin", "password": "adminpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
