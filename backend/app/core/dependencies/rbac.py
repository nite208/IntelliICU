from fastapi import Depends, HTTPException, status
from app.core.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.rbac_repository import RBACRepository

def require_roles(allowed_roles: list[str]):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role.lower() not in [r.lower() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: insufficient role privileges"
            )
        return current_user
    return dependency

def require_permission(required_permission: str):
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = RBACRepository.get_permissions_for_role(current_user.role)
        if required_permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: missing required permission '{required_permission}'"
            )
        return current_user
    return dependency
