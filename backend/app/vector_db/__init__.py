"""
app/vector_db/__init__.py

Vector Database Package.
Exposes the config settings and the thread-safe singleton ChromaService.
"""

from app.vector_db.config import CHROMA_DB_DIR, CHROMA_COLLECTION_NAME
from app.vector_db.chroma_service import ChromaService, chroma_service

__all__ = [
    "CHROMA_DB_DIR",
    "CHROMA_COLLECTION_NAME",
    "ChromaService",
    "chroma_service",
]
