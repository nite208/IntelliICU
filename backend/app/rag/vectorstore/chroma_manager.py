"""
ChromaDB Manager
"""

import chromadb
from chromadb.config import Settings

from app.rag.rag_config import (
    VECTOR_DB_DIR,
    COLLECTION_NAME,
)


class ChromaManager:
    """
    Enterprise ChromaDB Manager
    """

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR),
            settings=Settings(
                anonymized_telemetry=False,
            ),
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "IntelliICU Medical Knowledge Base",
            },
        )

    def add_documents(
        self,
        ids,
        documents,
        embeddings,
        metadatas,
    ):
        """
        Store document chunks in ChromaDB.
        """

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
        )

    def count(self):
        """
        Return total number of stored chunks.
        """

        return self.collection.count()

    def query(
        self,
        embedding,
        top_k=5,
    ):
        """
        Search the vector database for the most relevant chunks.
        """

        return self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )