from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from .core.config import settings
from .db import get_db
from . import models

# HTTP Bearer for paste-token flow in Swagger Authorize
bearer_scheme = HTTPBearer(auto_error=True)
ALGO = "HS256"

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = creds.credentials
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO])
        sub: str = payload.get("sub")
        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.get(models.User, int(sub))
    if not user:
        raise credentials_exception
    return user

def require_roles(*roles: models.Role):
    def checker(user: models.User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="insufficient role")
        return user
    return checker
