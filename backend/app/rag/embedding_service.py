"""
app/rag/embedding_service.py

Semantic embedding layer for IntelliICU.

This implementation is Railway-friendly:
- Model is NOT loaded during application startup.
- Model is loaded only when first needed.
- Prevents Railway OOM during boot.
"""

from __future__ import annotations

import logging
import threading
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

_MODEL_NAME = "BAAI/bge-small-en-v1.5"

_QUERY_PREFIX = (
    "Represent this sentence for searching relevant passages: "
)


class EmbeddingService:
    """
    Lazy-loading embedding service.
    """

    def __init__(self, model_name: str = _MODEL_NAME):

        self._model_name = model_name
        self._model = None
        self._lock = threading.Lock()

        self._ids: List[str] = []
        self._embeddings: Optional[np.ndarray] = None

    # ==========================================================
    # Internal
    # ==========================================================

    def _get_model(self):
        """
        Loads the embedding model only when required.
        """

        if self._model is None:

            with self._lock:

                if self._model is None:

                    logger.info(
                        "[EmbeddingService] Loading embedding model..."
                    )

                    from sentence_transformers import SentenceTransformer

                    self._model = SentenceTransformer(
                        self._model_name
                    )

                    logger.info(
                        "[EmbeddingService] Model loaded successfully."
                    )

        return self._model

    # ==========================================================
    # Indexing
    # ==========================================================

    def index_documents(
        self,
        ids: List[str],
        texts: List[str],
    ):

        if not texts:

            logger.warning(
                "[EmbeddingService] No documents supplied."
            )
            return

        model = self._get_model()

        logger.info(
            "[EmbeddingService] Creating embeddings for %d documents...",
            len(texts),
        )

        matrix = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

        self._ids = list(ids)

        self._embeddings = matrix.astype(np.float32)

        logger.info(
            "[EmbeddingService] Indexed %d documents.",
            len(self._ids),
        )

    # ==========================================================
    # Search
    # ==========================================================

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Tuple[str, float]]:

        if self._embeddings is None:

            logger.warning(
                "[EmbeddingService] Search attempted before indexing."
            )

            return []

        model = self._get_model()

        q = model.encode(
            _QUERY_PREFIX + query,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

        scores = self._embeddings @ q

        k = min(top_k, len(self._ids))

        idx = np.argpartition(scores, -k)[-k:]

        idx = idx[np.argsort(scores[idx])[::-1]]

        return [
            (
                self._ids[i],
                float(scores[i]),
            )
            for i in idx
        ]

    # ==========================================================
    # Properties
    # ==========================================================

    @property
    def is_ready(self):

        return (
            self._embeddings is not None
            and len(self._ids) > 0
        )

    @property
    def corpus_size(self):

        return len(self._ids)

    @property
    def model_name(self):

        return self._model_name