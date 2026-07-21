"""
app/api/rag.py

FastAPI API Router for Phase 14 AI Knowledge Platform (RAG).

Endpoints:
  POST   /api/rag/upload    → upload guidelines/documents (PDF, DOCX, TXT, MD) for parsing, chunking, and Chroma indexing
  GET    /api/rag/search    → perform hybrid query matching over vector DB + local fallback
  DELETE /api/rag/documents → delete chunks/files from vector store
  GET    /api/rag/documents → list all currently indexed chunks/documents
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.rag.knowledge_service import KnowledgeService
from app.rag.services.document_processor import DocumentProcessor
from app.vector_db.chroma_service import chroma_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/rag",
    tags=["RAG Knowledge Platform"],
)

# ---------------------------------------------------------------------------
# Lazy initialized document processor
# ---------------------------------------------------------------------------
_processor = None

def get_processor() -> DocumentProcessor:
    global _processor
    if _processor is None:
        # Re-use the existing embedder model from the KnowledgeService singleton
        # to avoid double memory footprint of sentence-transformers model.
        ks = KnowledgeService()
        _processor = DocumentProcessor(embedder=ks._embedder)
    return _processor


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SearchRequest(BaseModel):
    query:    str = Field(..., description="Guideline lookup query")
    top_k:    int = Field(default=5, description="Number of matches to return")
    category: Optional[str] = Field(default=None, description="Optional clinical category filter")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/upload", summary="Upload Clinical Document")
async def upload_document(
    title: str = Form(..., description="Guideline title"),
    source: str = Form(..., description="Authoring organization"),
    category: str = Form(..., description="Clinical domain category"),
    section: str = Form(..., description="Guideline sub-section"),
    tags: Optional[str] = Form(default="", description="Comma-separated keyword tags"),
    file: UploadFile = File(..., description="Clinical guideline file (.pdf, .docx, .txt, .md)"),
):
    """
    Ingest a clinical guideline file, extract its text content, split into overlapping chunks,
    generate vector embeddings using sentence-transformers, and persist to ChromaDB.
    """
    filename = file.filename or "uploaded_document"
    try:
        file_bytes = await file.read()
        tags_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

        processor = get_processor()
        chunk_ids = processor.process_and_index(
            file_bytes=file_bytes,
            filename=filename,
            title=title,
            source=source,
            category=category,
            section=section,
            tags=tags_list,
        )

        return {
            "status": "success",
            "filename": filename,
            "chunks_count": len(chunk_ids),
            "chunk_ids": chunk_ids,
        }
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        logger.error("[RAG API] Upload ingestion failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")


@router.get("/search", summary="Search Guidelines (Hybrid Search)")
def search_guidelines(
    query: str,
    top_k: int = 5,
    category: Optional[str] = None,
):
    """
    Execute a hybrid semantic query over clinical guidelines.
    Queries ChromaDB first, falling back to local memory on connection failure or empty results.
    """
    ks = KnowledgeService()
    results = ks.search(query=query, top_k=top_k, category=category)
    return {
        "query": query,
        "results_count": len(results),
        "results": results,
    }


@router.get("/documents", summary="List All Indexed Documents")
def list_documents():
    """
    List all documents currently registered in the vector store database.
    """
    try:
        results = chroma_service.get_all_documents()
        ids = results.get("ids", [])
        metadatas = results.get("metadatas", [])
        documents = results.get("documents", [])

        records = []
        for i in range(len(ids)):
            meta = metadatas[i] if i < len(metadatas) else {}
            doc_text = documents[i] if i < len(documents) else ""
            
            tags_str = meta.get("tags", "")
            tags = tags_str.split(",") if tags_str else []

            records.append({
                "chunk_id": ids[i],
                "title": meta.get("title", ""),
                "source": meta.get("source", ""),
                "category": meta.get("category", ""),
                "section": meta.get("section", ""),
                "filename": meta.get("filename", ""),
                "chunk_index": meta.get("chunk_index", 0),
                "tags": tags,
                "preview": doc_text[:200] + "..." if len(doc_text) > 200 else doc_text,
            })

        return {
            "status": "success",
            "total_chunks": len(records),
            "documents": records,
        }
    except Exception as exc:
        logger.error("[RAG API] Failed to list documents: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/documents/{identifier}", summary="Delete Document or Chunk")
def delete_document(identifier: str):
    """
    Remove documents/chunks from ChromaDB matching either the exact chunk ID
    or matching the 'filename' metadata.
    """
    try:
        # 1. Attempt chunk ID deletion
        success = chroma_service.delete_documents(ids=[identifier])
        
        # 2. Attempt filename metadata deletion (remove all chunks of the file)
        success_meta = chroma_service.delete_documents(where={"filename": identifier})

        if not success and not success_meta:
            raise HTTPException(status_code=404, detail=f"No matches found for identifier '{identifier}'")

        return {
            "status": "success",
            "message": f"Successfully deleted entries matching identifier '{identifier}'",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("[RAG API] Delete failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
