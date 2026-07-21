from pydantic import BaseModel

class Permission(BaseModel):
    id: str
    name: str  # e.g. "Dashboard", "Patients", etc.
    description: str | None = None

class Role(BaseModel):
    id: str
    name: str  # e.g. "SuperAdmin", "Doctor", etc.
    permissions: list[str] = []
