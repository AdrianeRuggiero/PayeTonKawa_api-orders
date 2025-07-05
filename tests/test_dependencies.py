import pytest
from fastapi import HTTPException
from app.security import dependencies

# Patch temporaire de verify_token
@pytest.fixture(autouse=True)
def reset_dependency_overrides():
    dependencies.verify_token = lambda token: {"sub": "user1", "role": "user"}
    yield
    dependencies.verify_token = lambda token: {"sub": "user1", "role": "user"}  # Reset

# get_current_user

def test_get_current_user_valid():
    user = dependencies.get_current_user(token="validtoken")
    assert user["sub"] == "user1"
    assert user["role"] == "user"

def test_get_current_user_invalid_token(monkeypatch):
    monkeypatch.setattr(dependencies, "verify_token", lambda token: None)
    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token="invalid")
    assert exc_info.value.status_code == 401

def test_get_current_user_missing_sub(monkeypatch):
    monkeypatch.setattr(dependencies, "verify_token", lambda token: {"role": "user"})
    with pytest.raises(HTTPException) as exc_info:
        dependencies.get_current_user(token="missing_sub")
    assert exc_info.value.status_code == 401

# require_role

def test_require_role_success():
    checker = dependencies.require_role("user")
    result = checker({"sub": "user1", "role": "user"})
    assert result["role"] == "user"

def test_require_role_forbidden():
    checker = dependencies.require_role("admin")
    with pytest.raises(HTTPException) as exc_info:
        checker({"sub": "user1", "role": "user"})
    assert exc_info.value.status_code == 403

# require_admin / require_user

def test_require_admin_allows_admin():
    admin_checker = dependencies.require_admin
    result = admin_checker({"sub": "admin", "role": "admin"})
    assert result["role"] == "admin"

def test_require_user_allows_user():
    user_checker = dependencies.require_user
    result = user_checker({"sub": "user1", "role": "user"})
    assert result["role"] == "user"

def test_require_admin_rejects_user():
    admin_checker = dependencies.require_admin
    with pytest.raises(HTTPException) as exc_info:
        admin_checker({"sub": "user1", "role": "user"})
    assert exc_info.value.status_code == 403
