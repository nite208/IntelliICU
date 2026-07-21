"""
RAG Configuration
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# ==============================
# Knowledge Base
# ==============================

KNOWLEDGE_BASE_DIR = (
    BASE_DIR
    / "app"
    / "rag"
    / "knowledge_base"
)

# ==============================
# Chroma Database
# ==============================

VECTOR_DB_DIR = (
    BASE_DIR
    / "vector_db"
)

COLLECTION_NAME = "intelliicu"

# ==============================
# Embedding Model
# ==============================

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

# ==============================
# Chunking
# ==============================

CHUNK_SIZE = 800

CHUNK_OVERLAP = 150

# ==============================
# Retrieval
# ==============================

TOP_K = 5
# ==============================
# Embedding
# ==============================

EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

DEVICE = "cpu"

# ==============================
# ChromaDB
# ==============================

VECTOR_DB_DIR = (
    BASE_DIR / "vector_db"
)

COLLECTION_NAME = "intelliicu_knowledge_base"