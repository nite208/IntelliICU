"""
app/vector_db/config.py

Configuration settings for the ChromaDB Vector Store.
Supports customizing paths and collection names via environment variables.
"""

import os
from pathlib import Path

# Base directory of the backend application
BASE_DIR = Path(__file__).resolve().parents[2]

# Directory where ChromaDB will persist its data
# Defaults to a "vector_db" directory in the backend root
CHROMA_DB_DIR = os.getenv(
    "CHROMA_PERSIST_DIRECTORY",
    str(BASE_DIR / "vector_db")
)

# Canonical collection name for indexing clinical guidelines
CHROMA_COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "intelliicu_knowledge_base"
)

# Default model used for embedding generation in RAG pipeline
EMBEDDING_MODEL_NAME = os.getenv(
    "CHROMA_EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5"
)
