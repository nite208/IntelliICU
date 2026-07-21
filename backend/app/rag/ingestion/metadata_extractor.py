"""
Enterprise Metadata Extractor
"""

from pathlib import Path
import re


class MetadataExtractor:
    """
    Builds clean metadata for IntelliICU RAG.
    """

    @staticmethod
    def _organization(filename: str):

        name = filename.lower()

        if "who" in name or "978924" in name:
            return "WHO"

        if "nice" in name:
            return "NICE"

        if "sepsis" in name:
            return "Surviving Sepsis Campaign"

        return "Medical Literature"

    @staticmethod
    def _year(filename: str):

        years = re.findall(r"(20\d{2})", filename)

        if years:
            return int(years[0])

        return None

    @staticmethod
    def extract(pdf_path: Path):

        folder = pdf_path.parent.name.lower()

        if folder == "guidelines":
            doc_type = "Guideline"

        elif folder == "protocols":
            doc_type = "Protocol"

        elif folder == "research_papers":
            doc_type = "Research Paper"

        else:
            doc_type = "Medical Document"

        return {
            "title": pdf_path.stem.replace("-", " "),
            "document_type": doc_type,
            "organization": MetadataExtractor._organization(
                pdf_path.name
            ),
            "year": MetadataExtractor._year(
                pdf_path.name
            ),
            "source_file": pdf_path.name,
            "source_path": str(pdf_path),
        }