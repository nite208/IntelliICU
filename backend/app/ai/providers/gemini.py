"""
Gemini LLM Provider.
Integrates Google Generative AI API with streaming capability support.
"""

import os
import json
import logging
from typing import Dict, Any, Generator

from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.mock import MockLLMProvider

logger = logging.getLogger(__name__)

class GeminiLLMProvider(BaseLLMProvider):
    """
    Connects to Google's Gemini models to analyze patient charts.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.mock_fallback = MockLLMProvider()

        if not self.api_key:
            logger.warning("GEMINI_API_KEY or GOOGLE_API_KEY not found. Falling back to MockProvider.")
            self.client = None
        else:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
            except ImportError:
                logger.warning("google-generativeai package not installed. Falling back to MockProvider.")
                self.client = None

    def generate(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.client:
            return self.mock_fallback.generate(question, context)

        prompt = (
            "You are an expert ICU Clinical Decision Support AI. Analyze the provided patient context and answer the clinical question.\n"
            "You MUST respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            "  \"reasoning\": \"Detailed reasoning explaining findings\",\n"
            "  \"risk_drivers\": [\"List of positive/negative features contributing to risk\"],\n"
            "  \"abnormal_vitals\": [\"List of out-of-range vital signs\"],\n"
            "  \"abnormal_labs\": [\"List of out-of-range lab results\"],\n"
            "  \"recommendations\": [\"Recommended clinical stabilization guidelines\"],\n"
            "  \"evidence\": [\"Biomarkers or reference data values justifying findings\"],\n"
            "  \"confidence\": 0.95\n"
            "}\n\n"
            f"Patient Clinical Context:\n{json.dumps(context, indent=2)}\n\n"
            f"Question:\n{question}\n\n"
            "Do not include markdown wrappers like ```json in the response."
        )

        try:
            response = self.client.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            raw_text = response.text
            data = json.loads(raw_text)
            
            # Map legacy fields for compatibility
            data["summary"] = data.get("reasoning", "")
            data["findings"] = data.get("risk_drivers", []) + data.get("abnormal_vitals", []) + data.get("abnormal_labs", [])
            data["risk"] = data.get("risk_drivers", ["Unknown"])[0] if data.get("risk_drivers") else "Unknown"
            
            return data
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}. Falling back to MockProvider.")
            return self.mock_fallback.generate(question, context)

    def generate_stream(self, question: str, context: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        if not self.client:
            yield from self.mock_fallback.generate_stream(question, context)
            return

        prompt = (
            "You are an expert ICU Clinical Decision Support AI. Analyze the provided patient context and answer the clinical question.\n"
            "You MUST respond ONLY with a valid JSON object matching this schema:\n"
            "{\n"
            "  \"reasoning\": \"Detailed reasoning explaining findings\",\n"
            "  \"risk_drivers\": [\"List of positive/negative features contributing to risk\"],\n"
            "  \"abnormal_vitals\": [\"List of out-of-range vital signs\"],\n"
            "  \"abnormal_labs\": [\"List of out-of-range lab results\"],\n"
            "  \"recommendations\": [\"Recommended clinical stabilization guidelines\"],\n"
            "  \"evidence\": [\"Biomarkers or reference data values justifying findings\"],\n"
            "  \"confidence\": 0.95\n"
            "}\n\n"
            f"Patient Clinical Context:\n{json.dumps(context, indent=2)}\n\n"
            f"Question:\n{question}\n\n"
            "Do not include markdown wrappers like ```json in the response."
        )

        try:
            # Simple stream wrapper for Gemini
            response = self.client.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"},
                stream=True
            )
            accumulated_text = ""
            for chunk in response:
                if chunk.text:
                    accumulated_text += chunk.text
                    yield {"type": "token", "content": chunk.text}

            try:
                data = json.loads(accumulated_text)
                data["summary"] = data.get("reasoning", "")
                data["findings"] = data.get("risk_drivers", []) + data.get("abnormal_vitals", []) + data.get("abnormal_labs", [])
                data["risk"] = data.get("risk_drivers", ["Unknown"])[0] if data.get("risk_drivers") else "Unknown"
                yield {"type": "final", "content": data}
            except Exception:
                yield {"type": "final", "content": self.mock_fallback.generate(question, context)}

        except Exception as e:
            logger.error(f"Gemini streaming failed: {e}. Falling back to MockProvider.")
            yield from self.mock_fallback.generate_stream(question, context)
