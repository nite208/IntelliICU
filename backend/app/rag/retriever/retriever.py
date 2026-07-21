"""
Enterprise Retriever for IntelliICU
"""

from app.rag.embeddings.embedding_service import EmbeddingService
from app.rag.vectorstore.chroma_manager import ChromaManager


class Retriever:
    """
    Semantic Retriever for IntelliICU.
    """

    def __init__(self):

        self.db = ChromaManager()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ):

        query_embedding = EmbeddingService.encode(
            [query]
        )[0]

        results = self.db.query(
            query_embedding,
            top_k,
        )

        response = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            response.append(
                {
                    "content": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return response