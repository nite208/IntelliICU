"""
Clinical RAG Service.
Exposes the retrieval layer for Guideline-backed clinical evidence.
"""

from typing import Dict, Any
from app.services.guideline_retriever import GuidelineRetriever

class ClinicalRAGService:
    """
    RAG service layer interfacing with the mock local clinical knowledge base.
    """

    def __init__(self):
        self.retriever = GuidelineRetriever()

    def process_rag_query(self, question: str) -> Dict[str, Any] | None:
        """
        Processes query against the guideline database.
        Returns the structured document if matched, otherwise None.
        """
        # Match topic
        match = self.retriever.retrieve(question)
        if match:
            return match
        return None
