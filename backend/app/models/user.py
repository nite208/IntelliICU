from pydantic import BaseModel

class User(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    role: str
    department: str | None = None
    is_active: bool = True
