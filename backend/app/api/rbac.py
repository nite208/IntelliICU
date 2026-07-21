from fastapi import APIRouter, Depends
from app.schemas.rbac import PermissionResponse, RoleResponse, UserPermissionsResponse
from app.repositories.rbac_repository import RBACRepository
from app.core.dependencies.auth import get_current_user
from app.core.dependencies.rbac import require_roles
from app.models.user import User

router = APIRouter(
    prefix="/rbac",
    tags=["Role-Based Access Control"],
)

@router.get("/roles", response_model=list[RoleResponse])
async def get_roles(
    current_user: User = Depends(require_roles(["SuperAdmin", "HospitalAdmin"]))
):
    return RBACRepository.get_all_roles()

@router.get("/permissions", response_model=list[PermissionResponse])
async def get_permissions(
    current_user: User = Depends(require_roles(["SuperAdmin", "HospitalAdmin"]))
):
    return RBACRepository.get_all_permissions()

@router.get("/users/me/permissions", response_model=UserPermissionsResponse)
async def get_my_permissions(
    current_user: User = Depends(get_current_user)
):
    permissions = RBACRepository.get_permissions_for_role(current_user.role)
    return {
        "role": current_user.role,
        "permissions": permissions
    }
