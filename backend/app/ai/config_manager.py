"""
app/ai/config_manager.py

Thread-safe, persistent configuration manager for the AI Provider Layer — Phase 15.
Allows changing config at runtime without restarting the application.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).resolve().parent / "ai_config.json"


class AIConfigManager:
    """
    Manages in-memory and on-disk persistent AI settings (provider, model, etc.).
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load settings from JSON config file on disk or fall back to env variables."""
        with self._lock:
            if CONFIG_PATH.exists():
                try:
                    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                        self._config = json.load(f)
                    logger.info("[AIConfigManager] Configuration loaded from %s", CONFIG_PATH)
                    return
                except Exception as e:
                    logger.error("[AIConfigManager] Failed to read config file: %s. Using env fallback.", e)

            # Fallback defaults
            provider = os.getenv("CLINICAL_LLM_PROVIDER", "mock").lower()
            default_model = "llama3" if provider == "ollama" else "mock-model"
            if provider == "openai":
                default_model = os.getenv("OPENAI_MODEL", "gpt-4")
            elif provider == "gemini":
                default_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")

            self._config = {
                "provider":    provider,
                "model":       os.getenv("CLINICAL_LLM_MODEL", default_model),
                "temperature": float(os.getenv("CLINICAL_LLM_TEMPERATURE", "0.2")),
                "max_tokens":  int(os.getenv("CLINICAL_LLM_MAX_TOKENS", "1024")),
                "streaming":   os.getenv("CLINICAL_LLM_STREAMING", "true").lower() == "true",
            }
            self.save_config()

    def save_config(self) -> None:
        """Write the current configuration to disk."""
        with self._lock:
            try:
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(self._config, f, indent=2)
                logger.info("[AIConfigManager] Configuration saved to %s", CONFIG_PATH)
            except Exception as e:
                logger.error("[AIConfigManager] Failed to write config file: %s", e)

    def get_all(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._config)

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._config.get(key, default)

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Merge updates into the configuration, validate fields, and save to disk.
        """
        with self._lock:
            # Type conversions & validation
            if "provider" in updates:
                self._config["provider"] = str(updates["provider"]).lower()
            if "model" in updates:
                self._config["model"] = str(updates["model"])
            if "temperature" in updates:
                self._config["temperature"] = max(0.0, min(2.0, float(updates["temperature"])))
            if "max_tokens" in updates:
                self._config["max_tokens"] = max(1, int(updates["max_tokens"]))
            if "streaming" in updates:
                self._config["streaming"] = bool(updates["streaming"])

            self.save_config()


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
ai_config = AIConfigManager()
