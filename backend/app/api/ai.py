"""
app/api/ai.py

FastAPI API Router for Phase 15 Local AI Platform.

Endpoints:
  GET /api/ai/providers → list all supported AI providers
  GET /api/ai/models    → list available models for the active/selected provider
  GET /api/ai/config    → fetch current runtime AI configuration settings
  PUT /api/ai/config    → update runtime configuration (provider, model, temp, etc.)
  GET /api/ai/health    → get health check status of the active AI provider
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.config_manager import ai_config
from app.ai.providers.ollama import OllamaLLMProvider
from app.ai.providers.openai_provider import OpenAILLMProvider
from app.ai.providers.gemini import GeminiLLMProvider
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.lmstudio import LMStudioLLMProvider

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["Local AI Platform"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AIConfigUpdateRequest(BaseModel):
    provider:    Optional[str] = Field(default=None, description="AI Provider name (mock, ollama, openai, gemini, lmstudio)")
    model:       Optional[str] = Field(default=None, description="Model identifier")
    temperature: Optional[float] = Field(default=None, description="Sampling temperature (0.0 to 2.0)")
    max_tokens:  Optional[int] = Field(default=None, description="Max response tokens")
    streaming:   Optional[bool] = Field(default=None, description="Enable response token streaming")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_provider_instance(provider_name: str):
    name = provider_name.lower()
    if name == "ollama":
        return OllamaLLMProvider()
    elif name == "openai":
        return OpenAILLMProvider()
    elif name == "gemini":
        return GeminiLLMProvider()
    elif name == "lmstudio":
        return LMStudioLLMProvider()
    return MockLLMProvider()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/providers", summary="List Supported Providers")
def get_providers():
    """List all supported AI model providers."""
    return {
        "status": "success",
        "providers": [
            {"id": "mock", "name": "Mock Clinical Provider (Default)", "local": True},
            {"id": "ollama", "name": "Ollama (Local Llama/Qwen)", "local": True},
            {"id": "openai", "name": "OpenAI (GPT-4/GPT-3.5)", "local": False},
            {"id": "gemini", "name": "Google Gemini (Pro/Flash)", "local": False},
            {"id": "lmstudio", "name": "LM Studio (Local Server)", "local": True},
        ]
    }


@router.get("/models", summary="List Available Models")
def get_models():
    """List available models for the currently selected AI provider."""
    provider_name = ai_config.get("provider", "mock")
    
    if provider_name == "ollama":
        provider = OllamaLLMProvider()
        models = provider.list_installed_models()
        if not models:
            models = ["llama3", "qwen2.5", "mistral"]
        return {"provider": "ollama", "models": models}
        
    elif provider_name == "openai":
        return {"provider": "openai", "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]}
        
    elif provider_name == "gemini":
        return {"provider": "gemini", "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"]}
        
    elif provider_name == "lmstudio":
        return {"provider": "lmstudio", "models": ["meta-llama-3-8b-instruct", "local-model"]}
        
    return {"provider": "mock", "models": ["mock-model"]}


@router.get("/config", summary="Get AI Settings")
def get_config():
    """Fetch current runtime AI configuration settings."""
    return {
        "status": "success",
        "config": ai_config.get_all()
    }


@router.put("/config", summary="Update AI Settings")
def update_config(request: AIConfigUpdateRequest):
    """Update runtime AI configurations (provider, model, temperature, etc.) immediately."""
    try:
        updates = {k: v for k, v in request.model_dump().items() if v is not None}
        ai_config.update(updates)
        return {
            "status": "success",
            "message": "AI settings updated successfully",
            "config": ai_config.get_all()
        }
    except Exception as e:
        logger.error("[AI API] Failed to update config: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Active Provider Health Check")
def get_health():
    """Perform health checks on the currently configured AI provider."""
    provider_name = ai_config.get("provider", "mock")
    provider = _get_provider_instance(provider_name)
    
    is_healthy = False
    details = ""
    
    if provider_name == "mock":
        is_healthy = True
        details = "Mock provider is always active."
    elif provider_name == "ollama":
        is_healthy = provider.health_check()
        details = "Ollama connection established." if is_healthy else "Ollama server offline or unreachable on default host."
    elif provider_name in ("openai", "gemini"):
        # Quick validation of keys
        has_client = getattr(provider, "client", None) is not None
        is_healthy = has_client
        details = f"{provider_name.upper()} client initialized successfully." if is_healthy else f"Client initialization failed; verify API keys."
    elif provider_name == "lmstudio":
        # LM Studio health check matches Ollama style (connect to models or root)
        try:
            model = provider._detect_model()
            is_healthy = model is not None
            details = f"LM Studio online; model: {model}" if is_healthy else "LM Studio offline."
        except Exception:
            is_healthy = False
            details = "LM Studio server offline or unreachable."
            
    return {
        "provider": provider_name,
        "healthy": is_healthy,
        "status": "healthy" if is_healthy else "unhealthy",
        "details": details
    }
