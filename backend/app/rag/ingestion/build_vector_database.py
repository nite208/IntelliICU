"""
Build IntelliICU Vector Database
"""

from app.rag.chunking.text_chunker import TextChunker
from app.rag.embeddings.embedding_service import EmbeddingService
from app.rag.loaders.pdf_loader import PDFLoader
from app.rag.vectorstore.chroma_manager import ChromaManager


def main():

    print("=" * 80)
    print("BUILDING INTELLIICU VECTOR DATABASE")
    print("=" * 80)

    docs = PDFLoader.load_documents()

    chunks = TextChunker().split_documents(
        docs
    )

    texts = [
        chunk.page_content
        for chunk in chunks
    ]

    embeddings = EmbeddingService.encode(
        texts
    )

    ids = [
        f"doc_{i}"
        for i in range(len(chunks))
    ]

    # ------------------------------------------------------------------
    # Clean metadata for ChromaDB
    # ChromaDB only accepts: str, int, float, bool
    # ------------------------------------------------------------------

    metadata = []

    for chunk in chunks:

        clean_metadata = {}

        for key, value in chunk.metadata.items():

            if value is None:
                continue

            if isinstance(value, (str, int, float, bool)):
                clean_metadata[key] = value
            else:
                clean_metadata[key] = str(value)

        metadata.append(clean_metadata)

    db = ChromaManager()

    db.add_documents(
        ids,
        texts,
        embeddings,
        metadata,
    )

    print()

    print("=" * 80)
    print("VECTOR DATABASE CREATED")
    print("=" * 80)

    print(f"Stored Chunks : {db.count()}")


if __name__ == "__main__":
    main()