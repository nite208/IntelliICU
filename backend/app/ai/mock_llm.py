"""
Mock Clinical LLM wrapper.
Maintains backward compatibility by forwarding calls to the active LLM provider, including streaming.
"""

from typing import Dict, Any, Generator
from app.ai.factory import get_llm_provider

class MockClinicalLLM:
    """
    Wrapper class forwarding clinical queries to the factory-resolved provider.
    """

    @staticmethod
    def generate_response(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Resolve provider dynamically at runtime
        provider = get_llm_provider()
        return provider.generate(question, context)

    @staticmethod
    def generate_stream(question: str, context: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        # Resolve provider dynamically at runtime
        provider = get_llm_provider()
        return provider.generate_stream(question, context)
