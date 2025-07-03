from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
from app.security.auth import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou utilisateur non authentifié",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_token(token)
    if not payload or payload.get("sub") is None:
        raise credentials_exception

    return {"sub": payload.get("sub"), "role": payload.get("role")}

def require_role(required_role: str):
    def checker(user: Dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit : rôle insuffisant"
            )
        return user
    return checker

# Accès direct par rôle
require_admin = require_role("admin")
require_user = require_role("user")
