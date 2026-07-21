from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str
    department: str | None = None

class UserUpdate(BaseModel):
    email: EmailStr
    role: str
    department: str | None = None
    is_active: bool = True

class PasswordReset(BaseModel):
    new_password: str = Field(..., min_length=6)

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class UserResponseSchema(BaseModel):
    id: str
    username: str
    email: str
    role: str
    department: str | None = None
    is_active: bool

class UserListResponse(BaseModel):
    users: list[UserResponseSchema]
    total: int
    page: int
    size: int
