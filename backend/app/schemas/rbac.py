from pydantic import BaseModel

class PermissionResponse(BaseModel):
    id: str
    name: str
    description: str | None = None

class RoleResponse(BaseModel):
    id: str
    name: str
    permissions: list[str] = []

class UserPermissionsResponse(BaseModel):
    role: str
    permissions: list[str] = []
