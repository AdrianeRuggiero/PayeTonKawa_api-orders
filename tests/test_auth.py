import pytest
from datetime import timedelta, datetime
from app.security.auth import create_access_token, verify_token

# Cas de base : génération et vérification d’un token valide
def test_create_and_verify_token():
    data = {"sub": "user1", "role": "user"}
    token = create_access_token(data)
    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == "user1"
    assert payload["role"] == "user"
    assert "exp" in payload

# Cas avec expiration personnalisée
def test_token_with_custom_expiry():
    data = {"sub": "admin", "role": "admin"}
    expires = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=expires)
    payload = verify_token(token)

    assert payload is not None
    assert payload["role"] == "admin"

# Cas : token malformé (pas un JWT)
def test_verify_invalid_token_format():
    invalid_token = "invalid.token.string"
    payload = verify_token(invalid_token)
    assert payload is None

# Cas : token avec signature cassée
def test_verify_token_with_invalid_signature():
    data = {"sub": "user1", "role": "user"}
    token = create_access_token(data)
    # on casse la signature en modifiant le token
    tampered = token + "abc"
    payload = verify_token(tampered)
    assert payload is None

# Cas : token valide mais payload invalide (sub ou role manquant)
def test_token_missing_claims():
    # Crée un token manuellement sans 'sub' et 'role'
    from jose import jwt
    from app.config import settings

    payload = {"exp": datetime.utcnow() + timedelta(minutes=10)}
    broken_token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    result = verify_token(broken_token)
    assert result is None
