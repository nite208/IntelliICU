"""
app/rag/services/document_processor.py

Intelligent Document Processor and Chunker for RAG — Phase 14.2.

Features:
  - Document parser: supports PDF (via pypdf), DOCX (via python-docx), TXT, and Markdown.
  - Intelligent character-based text chunker with paragraph and sentence boundary preservation.
  - Integration with existing EmbeddingService to compute 384-dimensional vector embeddings.
"""

from __future__ import annotations

import io
import logging
import re
from typing import Any, Dict, List, Optional

import pypdf
import docx

from app.rag.embedding_service import EmbeddingService
from app.vector_db.chroma_service import chroma_service

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Parses files, splits content into overlapping chunks, computes embeddings,
    and indexes them in ChromaDB.
    """

    def __init__(self, embedder: Optional[EmbeddingService] = None) -> None:
        # Re-use or lazily initialize the embedding service to avoid loading weights twice.
        self._embedder = embedder

    def _get_embedder(self) -> EmbeddingService:
        if self._embedder is None:
            self._embedder = EmbeddingService()
        return self._embedder

    # ------------------------------------------------------------------
    # Ingestion & In-Memory Extraction
    # ------------------------------------------------------------------

    def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """
        Extract text from file bytes based on file extension.
        """
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        if ext == "pdf":
            return self._extract_pdf(file_bytes)
        elif ext in ("docx", "doc"):
            return self._extract_docx(file_bytes)
        elif ext in ("txt", "md", "markdown"):
            return file_bytes.decode("utf-8", errors="ignore")
        else:
            raise ValueError(f"Unsupported file format: .{ext}")

    def _extract_pdf(self, file_bytes: bytes) -> str:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text_runs = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text()
            if txt:
                text_runs.append(txt)
        return "\n\n".join(text_runs)

    def _extract_docx(self, file_bytes: bytes) -> str:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    # ------------------------------------------------------------------
    # Text Chunker
    # ------------------------------------------------------------------

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 800,
        overlap: int = 150,
    ) -> List[str]:
        """
        Split a large text into overlapping chunks, respecting paragraph,
        sentence, and word boundaries.
        """
        cleaned = re.sub(r"\r", "", text).strip()
        if not cleaned:
            return []

        if len(cleaned) <= chunk_size:
            return [cleaned]

        chunks = []
        start = 0
        text_len = len(cleaned)

        while start < text_len:
            last_start = start
            end = min(start + chunk_size, text_len)

            # Try to align split on nice word/sentence/paragraph boundary
            if end < text_len:
                boundary = -1
                for separator in ["\n\n", "\n", ". ", " "]:
                    # Search backward in the last 120 characters of the window
                    idx = cleaned.rfind(separator, max(start, end - 120), end)
                    if idx != -1:
                        boundary = idx + len(separator)
                        break
                if boundary != -1:
                    end = boundary

            chunk = cleaned[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Next chunk start position
            start = end - overlap
            if start <= last_start or start >= text_len - overlap:
                # Safety guard: ensure loop moves forward
                start = end

        return chunks

    # ------------------------------------------------------------------
    # Chroma Indexing pipeline
    # ------------------------------------------------------------------

    def process_and_index(
        self,
        file_bytes: bytes,
        filename: str,
        title: str,
        source: str,
        category: str,
        section: str,
        tags: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Process a document: parse, chunk, embed, and index into ChromaDB.

        Returns
        -------
        List of generated chunk IDs.
        """
        # 1. Extract raw text
        raw_text = self.extract_text(file_bytes, filename)
        
        # 2. Split into chunks
        chunks = self.chunk_text(raw_text)
        if not chunks:
            logger.warning("[DocumentProcessor] No text chunks extracted from %s", filename)
            return []

        # 3. Generate embeddings & metadata
        embedder = self._get_embedder()
        chunk_ids = []
        metadatas = []
        embeddings = []
        
        tags_str = ",".join(tags) if tags else ""

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{filename.replace('.', '_')}_chunk_{idx}"
            chunk_ids.append(chunk_id)
            
            # Metadata parallel to documents
            metadatas.append({
                "title": title,
                "source": source,
                "category": category,
                "section": f"{section} (Part {idx + 1})",
                "tags": tags_str,
                "filename": filename,
                "chunk_index": idx,
            })
            
            # Generate 384-dimensional vector embedding
            emb = embedder._model.encode(
                chunk,
                normalize_embeddings=True,
                convert_to_numpy=True
            ).tolist()
            embeddings.append(emb)

        # 4. Upsert into ChromaDB
        success = chroma_service.add_documents(
            ids=chunk_ids,
            documents=chunks,
            metadatas=metadatas,
            embeddings=embeddings
        )

        if success:
            logger.info(
                "[DocumentProcessor] Ingested '%s': %d chunks indexed into ChromaDB.",
                filename, len(chunk_ids)
            )
            return chunk_ids
        else:
            raise RuntimeError(f"ChromaDB indexing failed for file '{filename}'")
