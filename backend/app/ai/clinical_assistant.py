"""
Enterprise Clinical AI Assistant
"""

from app.ai.llm_service import LLMService
from app.ai.prompt_builder import PromptBuilder
from app.rag.retriever.retriever import Retriever


class ClinicalAssistant:
    """
    Enterprise Retrieval-Augmented Clinical Assistant.
    """

    def __init__(self):

        self.retriever = Retriever()
        self.llm = LLMService()

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:

        retrieval_results = self.retriever.retrieve(
            query=question,
            top_k=top_k,
        )

        retrieved_chunks = [
            item["content"]
            for item in retrieval_results
        ]

        sources = [
            item["metadata"]
            for item in retrieval_results
        ]

        prompt = PromptBuilder.build(
            question=question,
            retrieved_chunks=retrieved_chunks,
        )

        answer = self.llm.generate(prompt)

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": len(retrieved_chunks),
        }