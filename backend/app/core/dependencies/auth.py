from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.models.user import User

# Using auth login endpoint as token url path
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception

    try:
        payload = AuthService.decode_token(token)
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        # Enforce that current user dependency requires access tokens only
        if username is None or token_type != "access":
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    user = UserRepository.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user
