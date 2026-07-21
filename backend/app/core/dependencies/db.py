from typing import Generator
from app.database.session import SessionLocal

def get_db() -> Generator:
    """
    FastAPI dependency that provides a SQLAlchemy session for requests.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
