"""
OpenAI LLM Provider.
Integrates OpenAI Chat Completion API with streaming and memory support.
"""

import os
import json
import logging
from typing import Dict, Any, Generator

from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.mock import MockLLMProvider

logger = logging.getLogger(__name__)

class OpenAILLMProvider(BaseLLMProvider):
    """
    Connects to OpenAI's GPT models to analyze patient charts.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.mock_fallback = MockLLMProvider()

        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment. Falling back to MockProvider.")
            self.client = None
        else:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("openai package not installed. Falling back to MockProvider.")
                self.client = None

    def generate(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.client:
            return self.mock_fallback.generate(question, context)

        system_prompt = (
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
            "}\n"
            "Do not include markdown tags like ```json in the raw response."
        )

        user_content = f"Patient Clinical Context:\n{json.dumps(context, indent=2)}\n\nQuestion:\n{question}"

        messages = context.get("conversation_history")
        if not messages:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content
            data = json.loads(raw_text)
            
            # Map legacy fields for compatibility
            data["summary"] = data.get("reasoning", "")
            data["findings"] = data.get("risk_drivers", []) + data.get("abnormal_vitals", []) + data.get("abnormal_labs", [])
            data["risk"] = data.get("risk_drivers", ["Unknown"])[0] if data.get("risk_drivers") else "Unknown"
            
            return data
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}. Falling back to MockProvider.")
            return self.mock_fallback.generate(question, context)

    def generate_stream(self, question: str, context: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        if not self.client:
            yield from self.mock_fallback.generate_stream(question, context)
            return

        system_prompt = (
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
            "}\n"
            "Do not include markdown tags like ```json in the raw response."
        )

        user_content = f"Patient Clinical Context:\n{json.dumps(context, indent=2)}\n\nQuestion:\n{question}"

        messages = context.get("conversation_history")
        if not messages:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                stream=True
            )
            accumulated_text = ""
            for chunk in response:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    token = delta.content
                    accumulated_text += token
                    yield {"type": "token", "content": token}

            try:
                data = json.loads(accumulated_text)
                data["summary"] = data.get("reasoning", "")
                data["findings"] = data.get("risk_drivers", []) + data.get("abnormal_vitals", []) + data.get("abnormal_labs", [])
                data["risk"] = data.get("risk_drivers", ["Unknown"])[0] if data.get("risk_drivers") else "Unknown"
                yield {"type": "final", "content": data}
            except Exception:
                yield {"type": "final", "content": self.mock_fallback.generate(question, context)}

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}. Falling back to MockProvider.")
            yield from self.mock_fallback.generate_stream(question, context)
