"""
Enterprise Text Chunker
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.rag_config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)


class TextChunker:
    """
    Creates semantic chunks for RAG.
    """

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=[
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

    def split_documents(
        self,
        documents,
    ):

        chunks = self.splitter.split_documents(
            documents
        )

        print("=" * 80)
        print("TEXT CHUNKING COMPLETED")
        print("=" * 80)

        print(f"\nInput Pages  : {len(documents)}")
        print(f"Output Chunks: {len(chunks)}")

        return chunks