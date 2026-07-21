from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.user_management import (
    UserCreate, UserUpdate, PasswordReset, PasswordChange,
    UserResponseSchema, UserListResponse
)
from app.models.user import User
from app.models.department import Department
from app.repositories.user_repository import UserRepository
from app.repositories.department_repository import DepartmentRepository
from app.services.auth_service import AuthService
from app.core.dependencies.auth import get_current_user
from app.core.dependencies.rbac import require_permission, require_roles
from app.services.timeline_engine import timeline_engine

router = APIRouter(
    prefix="/users",
    tags=["User Management"],
)

# Department route (separate sub-path)
dept_router = APIRouter(
    prefix="/departments",
    tags=["Departments"],
)

@dept_router.get("", response_model=list[Department])
async def get_departments(current_user: User = Depends(get_current_user)):
    return DepartmentRepository.get_all_departments()

@router.get("", response_model=UserListResponse)
async def list_users(
    search: str = Query(None),
    role: str = Query(None),
    department: str = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    current_user: User = Depends(require_permission("UserManagement"))
):
    users, total = UserRepository.list_users(search, role, department, page, size)
    # Convert list of User models to response schemas
    schemas = [
        UserResponseSchema(
            id=u.id,
            username=u.username,
            email=u.email,
            role=u.role,
            department=u.department,
            is_active=u.is_active
        )
        for u in users
    ]
    return {
        "users": schemas,
        "total": total,
        "page": page,
        "size": size
    }

@router.post("", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: User = Depends(require_permission("UserManagement"))
):
    try:
        hashed = AuthService.get_password_hash(payload.password)
        user = UserRepository.create_user({
            "username": payload.username,
            "email": payload.email,
            "hashed_password": hashed,
            "role": payload.role,
            "department": payload.department
        })
        
        # Audit admin action
        timeline_engine.add_event(
            patient_id="SYSTEM",
            event_type="User",
            title="User Account Created",
            description=f"Admin {current_user.username} created user account for {payload.username} ({payload.role}).",
            actor=current_user.username,
            metadata={"created_user": payload.username, "role": payload.role}
        )
        
        return UserResponseSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            department=user.department,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{user_id}", response_model=UserResponseSchema)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    current_user: User = Depends(require_permission("UserManagement"))
):
    try:
        user = UserRepository.update_user(user_id, {
            "email": payload.email,
            "role": payload.role,
            "department": payload.department,
            "is_active": payload.is_active
        })
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Audit admin action
        timeline_engine.add_event(
            patient_id="SYSTEM",
            event_type="User",
            title="User Account Updated",
            description=f"Admin {current_user.username} modified user account details for {user.username}.",
            actor=current_user.username,
            metadata={"updated_user_id": user_id, "is_active": payload.is_active}
        )
        
        return UserResponseSchema(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            department=user.department,
            is_active=user.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{user_id}", response_model=UserResponseSchema)
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_permission("UserManagement"))
):
    # Perform soft delete / deactivation only
    user = UserRepository.update_user(user_id, {"is_active": False})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Audit admin action
    timeline_engine.add_event(
        patient_id="SYSTEM",
        event_type="User",
        title="User Account Deactivated",
        description=f"Admin {current_user.username} soft-deleted/deactivated account {user.username}.",
        actor=current_user.username,
        metadata={"deactivated_user_id": user_id}
    )
    
    return UserResponseSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        department=user.department,
        is_active=user.is_active
    )

@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: str,
    payload: PasswordReset,
    current_user: User = Depends(require_permission("UserManagement"))
):
    user = UserRepository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    hashed = AuthService.get_password_hash(payload.new_password)
    success = UserRepository.set_password(user_id, hashed)
    
    # Audit admin action
    timeline_engine.add_event(
        patient_id="SYSTEM",
        event_type="User",
        title="Administrative Password Reset",
        description=f"Admin {current_user.username} initiated password reset for user {user.username}.",
        actor=current_user.username,
        metadata={"reset_user_id": user_id}
    )
    
    return {"success": success, "message": "Password reset successfully completed."}

@router.post("/me/change-password")
async def change_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_user)
):
    # Verify old password
    if not AuthService.verify_password(payload.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password provided.")
        
    hashed = AuthService.get_password_hash(payload.new_password)
    success = UserRepository.set_password(current_user.id, hashed)
    
    # Audit self-service action
    timeline_engine.add_event(
        patient_id="SYSTEM",
        event_type="User",
        title="User Password Changed",
        description=f"User {current_user.username} successfully updated their login password.",
        actor=current_user.username,
        metadata={"user_id": current_user.id}
    )
    
    return {"success": success, "message": "Your password has been changed successfully."}
