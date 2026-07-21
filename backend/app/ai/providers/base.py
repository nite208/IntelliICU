"""
Base LLM Provider Interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Generator

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for clinical LLM providers.
    """

    @abstractmethod
    def generate(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes query analysis and returns explainable clinical parameters.
        """
        pass

    @abstractmethod
    def generate_stream(self, question: str, context: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        Generates streaming output chunks during clinical reasoning.
        """
        pass
