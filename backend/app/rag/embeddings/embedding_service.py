"""
Embedding Service
"""

from sentence_transformers import SentenceTransformer

from app.rag.rag_config import (
    DEVICE,
    EMBEDDING_MODEL,
)


class EmbeddingService:
    """
    Enterprise embedding service.
    """

    _model = None

    @classmethod
    def load_model(cls):

        if cls._model is None:

            print("=" * 80)
            print("LOADING EMBEDDING MODEL")
            print("=" * 80)

            cls._model = SentenceTransformer(
                EMBEDDING_MODEL,
                device=DEVICE,
            )

            print("Embedding Model Loaded")

        return cls._model

    @classmethod
    def encode(cls, texts):

        model = cls.load_model()

        return model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True,
        )
    