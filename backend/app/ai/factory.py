"""
Clinical LLM Provider Factory.
"""

import os
import logging
from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.openai_provider import OpenAILLMProvider
from app.ai.providers.gemini import GeminiLLMProvider
from app.ai.providers.ollama import OllamaLLMProvider
from app.ai.providers.lmstudio import LMStudioLLMProvider

from app.ai.config_manager import ai_config

logger = logging.getLogger(__name__)

def get_llm_provider() -> BaseLLMProvider:
    """
    Selects and returns the configured clinical LLM provider based on dynamic settings.
    """
    provider_type = ai_config.get("provider", "mock").lower()

    if provider_type == "openai":
        provider = OpenAILLMProvider()
        if provider.client is None:
            logger.warning("OpenAI client missing key or SDK. Defaulting to MockLLMProvider.")
            return MockLLMProvider()
        return provider

    elif provider_type == "gemini":
        provider = GeminiLLMProvider()
        if provider.client is None:
            logger.warning("Gemini client missing key or SDK. Defaulting to MockLLMProvider.")
            return MockLLMProvider()
        return provider

    elif provider_type == "ollama":
        provider = OllamaLLMProvider()
        # Verify connection health; fallback if offline
        if not provider.health_check():
            logger.warning("Ollama provider is configured but connection failed. Defaulting to MockLLMProvider.")
            return MockLLMProvider()
        return provider

    elif provider_type == "lmstudio":
        return LMStudioLLMProvider()

    # Default fallback
    return MockLLMProvider()
