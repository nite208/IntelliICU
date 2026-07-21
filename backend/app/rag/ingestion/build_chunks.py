"""
Chunk Builder
"""

from app.rag.chunking.text_chunker import TextChunker
from app.rag.loaders.pdf_loader import PDFLoader


def main():

    print("=" * 80)
    print("INTELLIICU CHUNK PIPELINE")
    print("=" * 80)

    documents = PDFLoader.load_documents()

    chunker = TextChunker()

    chunks = chunker.split_documents(
        documents
    )

    print()

    print("=" * 80)
    print("FIRST CHUNK")
    print("=" * 80)

    print(chunks[0].page_content)

    print()

    print("=" * 80)
    print("FIRST CHUNK METADATA")
    print("=" * 80)

    print(chunks[0].metadata)


if __name__ == "__main__":
    main()