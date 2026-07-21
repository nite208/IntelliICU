from pydantic import BaseModel

class Department(BaseModel):
    id: str
    name: str
    description: str | None = None
