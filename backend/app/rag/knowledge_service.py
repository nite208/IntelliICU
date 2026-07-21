"""
app/rag/knowledge_service.py

In-memory Clinical Knowledge Service — Phase 12.4: Semantic Retrieval.

Search strategy
---------------
Primary  : Embedding-based cosine similarity (BAAI/bge-small-en-v1.5)
Fallback : Keyword scoring

Production safety
-----------------
Semantic embeddings can be disabled with:

    ENABLE_SEMANTIC_EMBEDDINGS=false

This is useful for memory-constrained deployments such as Railway.
When disabled, the application does NOT load sentence-transformers or
the Hugging Face embedding model and automatically uses keyword search.

The public API remains unchanged:
    load_documents()
    search(query)
    get_by_id(id)
    list_categories()
    count()
"""

from __future__ import annotations

import logging
import os
import re
from typing import Dict, List, Optional

from app.rag.document import ClinicalDocument
from app.rag.sources import ALL_CLINICAL_DOCUMENTS

logger = logging.getLogger(__name__)


class KnowledgeService:
    """
    Singleton-friendly in-memory clinical knowledge service.

    Semantic retrieval is enabled by default unless explicitly disabled
    using the ENABLE_SEMANTIC_EMBEDDINGS environment variable.

    If semantic embeddings are disabled or fail to initialize, the service
    automatically falls back to keyword search.
    """

    def __init__(self) -> None:
        self._store: Dict[str, ClinicalDocument] = {}
        self._embedder = None
        self._semantic_ready = False

        self._semantic_enabled = (
            os.getenv("ENABLE_SEMANTIC_EMBEDDINGS", "true")
            .strip()
            .lower()
            in {"1", "true", "yes", "on"}
        )

        if self._semantic_enabled:
            logger.info(
                "[KnowledgeService] Semantic embeddings enabled."
            )
        else:
            logger.info(
                "[KnowledgeService] Semantic embeddings disabled — "
                "using keyword search."
            )

        self.load_documents()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_documents(
        self,
        extra: Optional[List[ClinicalDocument]] = None,
    ) -> None:
        """
        Load the default corpus plus any caller-supplied documents.

        If semantic embeddings are enabled, rebuild the embedding index.
        Otherwise, keep keyword-search mode active.
        """

        docs = ALL_CLINICAL_DOCUMENTS + (extra or [])

        self._store = {
            doc.id: doc
            for doc in docs
        }

        logger.info(
            "[KnowledgeService] Loaded %d clinical documents.",
            len(self._store),
        )

        if self._semantic_enabled:
            self._build_embedding_index()
        else:
            self._semantic_ready = False
            self._embedder = None

            logger.info(
                "[KnowledgeService] Skipping embedding model initialization."
            )

    def search(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None,
    ) -> List[Dict]:
        """
        Return the top-k most relevant documents.

        Search order:

        1. ChromaDB + semantic embeddings, when embeddings are available.
        2. In-memory semantic search.
        3. Keyword search fallback.

        ChromaDB semantic querying is skipped when the local embedding
        model is disabled because no query embedding can be generated.
        """

        if not query:
            return []

        # --------------------------------------------------------------
        # 1. ChromaDB semantic search
        # --------------------------------------------------------------

        if self._semantic_ready and self._embedder is not None:

            try:
                from app.vector_db.chroma_service import chroma_service

                if chroma_service.health_check():

                    from app.rag.embedding_service import _QUERY_PREFIX

                    q_vec = self._embedder._model.encode(
                        _QUERY_PREFIX + query,
                        normalize_embeddings=True,
                        convert_to_numpy=True,
                    ).tolist()

                    where_filter = None

                    if category:
                        where_filter = {
                            "category": category
                        }

                    res = chroma_service.query_documents(
                        query_embeddings=q_vec,
                        n_results=top_k,
                        where=where_filter,
                    )

                    docs = []

                    if (
                        res
                        and res.get("ids")
                        and len(res["ids"]) > 0
                        and len(res["ids"][0]) > 0
                    ):

                        for i in range(len(res["ids"][0])):

                            doc_id = res["ids"][0][i]

                            distance = (
                                res["distances"][0][i]
                                if "distances" in res
                                else 0.0
                            )

                            sim_score = max(
                                0.0,
                                min(
                                    1.0,
                                    1.0 - (distance / 2.0),
                                ),
                            )

                            metadata = (
                                res["metadatas"][0][i]
                                if "metadatas" in res
                                else {}
                            )

                            content = (
                                res["documents"][0][i]
                                if "documents" in res
                                else ""
                            )

                            tags_raw = metadata.get(
                                "tags",
                                "",
                            )

                            tags = (
                                tags_raw.split(",")
                                if isinstance(tags_raw, str)
                                and tags_raw
                                else []
                            )

                            docs.append(
                                {
                                    "id": doc_id,
                                    "title": metadata.get(
                                        "title",
                                        "",
                                    ),
                                    "source": metadata.get(
                                        "source",
                                        metadata.get(
                                            "organization",
                                            "",
                                        ),
                                    ),
                                    "category": metadata.get(
                                        "category",
                                        "",
                                    ),
                                    "section": metadata.get(
                                        "section",
                                        "",
                                    ),
                                    "content": content,
                                    "tags": tags,
                                    "score": round(
                                        sim_score,
                                        4,
                                    ),
                                }
                            )

                        if docs:

                            logger.info(
                                "[KnowledgeService] "
                                "ChromaDB returned %d results.",
                                len(docs),
                            )

                            return docs

            except Exception as exc:

                logger.warning(
                    "[KnowledgeService] ChromaDB query failed; "
                    "falling back: %s",
                    exc,
                )

        # --------------------------------------------------------------
        # 2. In-memory semantic search
        # --------------------------------------------------------------

        if self._semantic_ready and self._embedder is not None:

            return self._semantic_search(
                query,
                top_k,
                category,
            )

        # --------------------------------------------------------------
        # 3. Keyword fallback
        # --------------------------------------------------------------

        return self._keyword_search(
            query,
            top_k,
            category,
        )

    def get_by_id(
        self,
        doc_id: str,
    ) -> Optional[ClinicalDocument]:

        return self._store.get(doc_id)

    def list_categories(self) -> List[str]:

        return sorted(
            {
                doc.category
                for doc in self._store.values()
            }
        )

    def count(self) -> int:

        return len(self._store)

    @property
    def search_mode(self) -> str:
        """
        Current retrieval mode.

        Returns:
            semantic
            keyword
        """

        if self._semantic_ready:
            return "semantic"

        return "keyword"

    # ------------------------------------------------------------------
    # Embedding bootstrap
    # ------------------------------------------------------------------

    def _build_embedding_index(self) -> None:
        """
        Build the semantic embedding index.

        Any failure automatically switches the service to keyword mode.
        """

        if not self._semantic_enabled:

            logger.info(
                "[KnowledgeService] Semantic embeddings disabled — "
                "embedding index will not be built."
            )

            self._semantic_ready = False
            self._embedder = None

            return

        try:

            from app.rag.embedding_service import EmbeddingService

            if self._embedder is None:
                self._embedder = EmbeddingService()

            ids = list(
                self._store.keys()
            )

            texts = [
                f"{doc.title}. "
                f"{doc.section}. "
                f"{doc.content}"
                for doc in self._store.values()
            ]

            self._embedder.index_documents(
                ids,
                texts,
            )

            self._semantic_ready = (
                self._embedder.is_ready
            )

            logger.info(
                "[KnowledgeService] Embedding index ready — "
                "%d vectors (model: %s)",
                self._embedder.corpus_size,
                self._embedder.model_name,
            )

        except ImportError as exc:

            logger.warning(
                "[KnowledgeService] Semantic embedding dependency "
                "unavailable (%s) — using keyword search.",
                exc,
            )

            self._embedder = None
            self._semantic_ready = False

        except Exception as exc:

            logger.warning(
                "[KnowledgeService] Embedding index build failed "
                "(%s) — using keyword search.",
                exc,
            )

            self._embedder = None
            self._semantic_ready = False

    # ------------------------------------------------------------------
    # Intent inference
    # ------------------------------------------------------------------

    def _infer_intent(
        self,
        query: str,
    ) -> dict:

        query_lower = query.lower()

        boosts = {
            "categories": {},
            "tags": [
                word
                for word in re.sub(
                    r"[^a-z0-9]",
                    " ",
                    query_lower,
                ).split()
                if len(word) > 2
            ],
        }

        # Drug intent

        drug_keywords = [
            "dose",
            "dosing",
            "renal adjustment",
            "indication",
            "adverse effect",
            "side effect",
            "interaction",
            "contraindication",
            "mechanism",
        ]

        drug_names = [
            "norepinephrine",
            "vasopressin",
            "epinephrine",
            "dobutamine",
            "meropenem",
            "piperacillin",
            "tazobactam",
            "vancomycin",
            "furosemide",
            "drug",
        ]

        if (
            any(k in query_lower for k in drug_keywords)
            or any(d in query_lower for d in drug_names)
        ):
            boosts["categories"]["drug"] = 0.25

        # Sepsis / shock intent

        sepsis_keywords = [
            "sepsis",
            "septic",
            "shock",
            "infection",
            "antibiotic",
            "lactate",
            "surviving sepsis",
            "ssc",
        ]

        if any(
            k in query_lower
            for k in sepsis_keywords
        ):
            boosts["categories"]["sepsis"] = 0.08
            boosts["categories"]["shock"] = 0.04

        # AKI intent

        aki_keywords = [
            "aki",
            "kidney",
            "renal",
            "creatinine",
            "urine",
            "kdigo",
            "dialysis",
            "rrt",
            "hyperkalemia",
            "bun",
            "lasix",
            "furosemide",
        ]

        if any(
            k in query_lower
            for k in aki_keywords
        ):

            boosts["categories"]["aki"] = 0.12

            if any(
                word in query_lower
                for word in [
                    "diagnosis",
                    "detect",
                    "stage",
                    "criteria",
                ]
            ):
                boosts["categories"]["aki"] += 0.05

        # Oxygen / respiratory intent

        oxygen_keywords = [
            "oxygen",
            "spo2",
            "pao2",
            "hypoxia",
            "hyperoxia",
            "respiratory",
            "ventilation",
            "ventilator",
            "hfno",
            "niv",
            "breathing",
            "cyanosis",
        ]

        if any(
            k in query_lower
            for k in oxygen_keywords
        ):
            boosts["categories"][
                "oxygen therapy"
            ] = 0.12

        return boosts

    # ------------------------------------------------------------------
    # Semantic search
    # ------------------------------------------------------------------

    def _semantic_search(
        self,
        query: str,
        top_k: int,
        category: Optional[str],
    ) -> List[Dict]:

        if (
            not self._semantic_ready
            or self._embedder is None
        ):
            return self._keyword_search(
                query,
                top_k,
                category,
            )

        hits = self._embedder.search(
            query,
            top_k=self.count(),
        )

        boosts = self._infer_intent(
            query
        )

        scored_docs = []

        for doc_id, semantic_score in hits:

            doc = self._store.get(
                doc_id
            )

            if doc is None:
                continue

            if (
                category
                and doc.category.lower()
                != category.lower()
            ):
                continue

            cat_boost = boosts[
                "categories"
            ].get(
                doc.category.lower(),
                0.0,
            )

            title_lower = (
                doc.title.lower()
            )

            title_matches = sum(
                1
                for term in boosts["tags"]
                if term in title_lower
            )

            title_boost = min(
                title_matches * 0.01,
                0.05,
            )

            doc_tags_lower = [
                tag.lower()
                for tag in doc.tags
            ]

            tag_matches = sum(
                1
                for term in boosts["tags"]
                if any(
                    term in tag
                    or tag in term
                    for tag in doc_tags_lower
                )
            )

            tag_boost = min(
                tag_matches * 0.01,
                0.04,
            )

            final_score = min(
                semantic_score
                + cat_boost
                + title_boost
                + tag_boost,
                1.0,
            )

            entry = doc.to_dict()

            entry["score"] = round(
                final_score,
                4,
            )

            scored_docs.append(
                entry
            )

        scored_docs.sort(
            key=lambda x: (
                -x["score"],
                x["id"],
            )
        )

        return scored_docs[:top_k]

    # ------------------------------------------------------------------
    # Keyword search
    # ------------------------------------------------------------------

    def _keyword_search(
        self,
        query: str,
        top_k: int,
        category: Optional[str],
    ) -> List[Dict]:

        terms = self._tokenise(
            query
        )

        if not terms:
            return []

        scored: List[tuple] = []

        for doc in self._store.values():

            if (
                category
                and doc.category.lower()
                != category.lower()
            ):
                continue

            score = self._score(
                doc,
                terms,
            )

            if score > 0:
                scored.append(
                    (
                        score,
                        doc,
                    )
                )

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1].id,
            )
        )

        results = []

        for score, doc in scored[:top_k]:

            entry = doc.to_dict()

            entry["score"] = round(
                score,
                4,
            )

            results.append(
                entry
            )

        logger.debug(
            "[KnowledgeService] Keyword search: %r → %d results",
            query,
            len(results),
        )

        return results

    # ------------------------------------------------------------------
    # Keyword helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenise(
        text: str,
    ) -> List[str]:

        raw = re.sub(
            r"[^a-z0-9\s]",
            " ",
            text.lower(),
        )

        return list(
            {
                word
                for word in raw.split()
                if len(word) > 2
            }
        )

    def _score(
        self,
        doc: ClinicalDocument,
        terms: List[str],
    ) -> float:

        score = 0.0

        content_lower = (
            doc.content.lower()
        )

        title_lower = (
            doc.title.lower()
        )

        tags_lower = [
            tag.lower()
            for tag in doc.tags
        ]

        category_lower = (
            doc.category.lower()
        )

        content_len = max(
            len(
                content_lower.split()
            ),
            1,
        )

        for term in terms:

            tf = (
                content_lower.count(term)
                / content_len
            )

            score += tf

            if term in title_lower:
                score += 1.5

            if term in category_lower:
                score += 3.0

            for tag in tags_lower:

                if (
                    term == tag
                    or term in tag.split()
                ):
                    score += 2.0
                    break

        return score