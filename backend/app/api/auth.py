from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, RefreshRequest
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.core.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.user_management import UserCreate
from app.database.session import SessionLocal
from app.database.models import DBUser

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/bootstrap", response_model=UserResponse)
async def bootstrap_first_admin(payload: UserCreate):
    """
    Bootstrap the first administrator account if no users currently exist in the system database.
    This automatically disables itself once at least one user is present.
    """
    db = SessionLocal()
    try:
        user_count = db.query(DBUser).count()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bootstrap is disabled: users already exist in the database."
            )
            
        if payload.role not in ["HospitalAdmin", "SuperAdmin"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bootstrap user must be an administrative role (HospitalAdmin or SuperAdmin)."
            )
            
        hashed = AuthService.get_password_hash(payload.password)
        user = UserRepository.create_user({
            "username": payload.username,
            "email": payload.email,
            "hashed_password": hashed,
            "role": payload.role,
            "department": payload.department
        })
        
        return user
    except ValueError as val_err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_err))
    finally:
        db.close()

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = AuthService.authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token = AuthService.create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh(payload: RefreshRequest):
    try:
        dec = AuthService.decode_token(payload.refresh_token)
        username = dec.get("sub")
        token_type = dec.get("type")
        
        # Enforce token type must be refresh token
        if not username or token_type != "refresh":
            raise ValueError()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
        
    user = UserRepository.get_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    access_token = AuthService.create_access_token(data={"sub": user.username, "role": user.role})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }

@router.post("/logout")
async def logout():
    return {"success": True, "message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
