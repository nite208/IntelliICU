"""
Enterprise PDF Loader
"""

from langchain_community.document_loaders import PyPDFLoader

from app.rag.ingestion.document_cleaner import DocumentCleaner
from app.rag.ingestion.metadata_extractor import MetadataExtractor
from app.rag.rag_config import KNOWLEDGE_BASE_DIR


class PDFLoader:
    """
    Loads all medical PDFs.
    """

    @staticmethod
    def load_documents():

        pdf_files = list(
            KNOWLEDGE_BASE_DIR.rglob("*.pdf")
        )

        documents = []

        print("=" * 80)
        print("INTELLIICU KNOWLEDGE INGESTION")
        print("=" * 80)

        print(f"\nPDF Files Found : {len(pdf_files)}\n")

        for pdf in pdf_files:

            print(f"Loading : {pdf.name}")

            loader = PyPDFLoader(
                str(pdf)
            )

            docs = loader.load()

            metadata = MetadataExtractor.extract(
                pdf
            )

            for doc in docs:

                # Clean the extracted text
                doc.page_content = DocumentCleaner.clean(
                    doc.page_content
                )

                # Keep only enterprise metadata
                clean_metadata = {
                    "title": metadata["title"],
                    "document_type": metadata["document_type"],
                    "organization": metadata["organization"],
                    "year": metadata["year"],
                    "page": doc.metadata.get("page", 0),
                    "source_file": metadata["source_file"],
                    "source_path": metadata["source_path"],
                }

                # Replace noisy PDF metadata
                doc.metadata = clean_metadata

            documents.extend(
                docs
            )

        print()

        print("=" * 80)
        print(f"Total Pages Loaded : {len(documents)}")
        print("=" * 80)

        return documents


if __name__ == "__main__":

    docs = PDFLoader.load_documents()

    print()

    print("=" * 80)
    print("SAMPLE METADATA")
    print("=" * 80)

    print(docs[0].metadata)

    print()

    print("=" * 80)
    print("SAMPLE TEXT")
    print("=" * 80)

    print(docs[0].page_content[:500])