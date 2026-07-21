"""
LM Studio LLM Provider.
Integrates local LM Studio instances via OpenAI-compatible HTTP API with advanced context optimization, memory, caching, and streaming metrics.
"""

import os
import json
import logging
import urllib.request
import time
import sys
import traceback
from typing import Dict, Any, Generator

from app.ai.providers.base import BaseLLMProvider
from app.ai.providers.mock import MockLLMProvider
from app.services.context_optimizer import ContextOptimizer

logger = logging.getLogger(__name__)

class LMStudioLLMProvider(BaseLLMProvider):
    """
    Connects to local LM Studio instances to analyze patient charts.
    """

    def __init__(self):
        self.base_url = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1").rstrip("/")
        self.mock_fallback = MockLLMProvider()

    def _detect_model(self) -> str:
        """
        Queries LM Studio models endpoint to detect the currently loaded model.
        """
        try:
            req = urllib.request.Request(
                f"{self.base_url}/models",
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=3.0) as response:
                body = response.read().decode("utf-8")
                data = json.loads(body)
                if data.get("data") and len(data["data"]) > 0:
                    model_id = data["data"][0]["id"]
                    return model_id
        except Exception as e:
            logger.warning(f"Failed to auto-detect LM Studio model: {e}. Using default.")
        
        return os.getenv("LMSTUDIO_MODEL", "meta-llama-3-8b-instruct")

    def generate(self, question: str, context: Dict[str, Any]) -> Dict[str, Any]:
        print("[DEBUG] Selected provider: LMStudioProvider", flush=True)
        
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
            "Do not include markdown tags."
        )

        # 1. Determine prompt source (memory vs context)
        messages = context.get("conversation_history") if isinstance(context, dict) else None
        char_count = 0
        est_tokens = 0

        if not messages:
            # Optimize context
            optimized_context = ContextOptimizer.optimize(context)
            opt_context_str = json.dumps(optimized_context, indent=2)
            user_content = f"Patient Clinical Context:\n{opt_context_str}\n\nQuestion:\n{question}"
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            char_count = len(system_prompt + user_content)
            est_tokens = char_count // 4
        else:
            print("[DEBUG] Conversation Memory hit! Reusing history.", flush=True)
            prompt_json = json.dumps(messages)
            char_count = len(prompt_json)
            est_tokens = char_count // 4

        # 2. Detect model
        model_id = self._detect_model()
        print(f"[DEBUG] Detected model: {model_id}", flush=True)
        print(f"[DEBUG] Prompt size - Characters: {char_count}, Estimated Tokens: {est_tokens}", flush=True)

        max_tokens = context.get("performance_metrics", {}).get("max_tokens", 400) if isinstance(context, dict) else 400

        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens
        }

        start_time = time.time()
        print(f"[DEBUG] Sending request to LM Studio at timestamp: {start_time}", flush=True)

        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=180.0) as response:
                end_time = time.time()
                elapsed = end_time - start_time
                print(f"[DEBUG] Response received in {elapsed:.2f}s", flush=True)

                body = response.read().decode("utf-8")
                res_data = json.loads(body)
                raw_text = res_data["choices"][0]["message"]["content"]
                data = json.loads(raw_text)

                # Map legacy fields for compatibility
                data["summary"] = data.get("reasoning", "")
                data["findings"] = data.get("risk_drivers", []) + data.get("abnormal_vitals", []) + data.get("abnormal_labs", [])
                data["risk"] = data.get("risk_drivers", ["Unknown"])[0] if data.get("risk_drivers") else "Unknown"

                # Attach performance metrics
                data["performance_metrics"] = {
                    "cache": context.get("performance_metrics", {}).get("cache", "MISS") if isinstance(context, dict) else "MISS",
                    "prompt_size_chars": char_count,
                    "estimated_tokens": est_tokens,
                    "prompt_evaluation_time_ms": int(elapsed * 0.4 * 1000), # approximation for non-stream
                    "generation_time_ms": int(elapsed * 0.6 * 1000),
                    "tokens_per_sec": round((res_data.get("usage", {}).get("completion_tokens", 100) / max(1, elapsed)), 1),
                    "total_response_time_ms": int(elapsed * 1000)
                }

                print("INFO: Request served by: LMStudioProvider", flush=True)
                return data
        except Exception as e:
            logger.warning(f"LM Studio completion failed: {e}. Falling back to MockProvider.")
            return self.mock_fallback.generate(question, context)

    def generate_stream(self, question: str, context: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        print("[DEBUG] Selected provider (streaming): LMStudioProvider", flush=True)

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
            "Do not include markdown tags."
        )

        # 1. Determine prompt source (memory vs context)
        messages = context.get("conversation_history") if isinstance(context, dict) else None
        char_count = 0
        est_tokens = 0

        if not messages:
            # Optimize context
            optimized_context = ContextOptimizer.optimize(context)
            opt_context_str = json.dumps(optimized_context, indent=2)
            user_content = f"Patient Clinical Context:\n{opt_context_str}\n\nQuestion:\n{question}"
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
            char_count = len(system_prompt + user_content)
            est_tokens = char_count // 4
        else:
            print("[DEBUG] Conversation Memory hit! Reusing history.", flush=True)
            prompt_json = json.dumps(messages)
            char_count = len(prompt_json)
            est_tokens = char_count // 4

        # 2. Detect model
        model_id = self._detect_model()
        print(f"[DEBUG] Detected model: {model_id}", flush=True)

        # 3. Payload Construction
        max_tokens = context.get("performance_metrics", {}).get("max_tokens", 400) if isinstance(context, dict) else 400
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens,
            "stream": True
        }

        start_time = time.time()
        first_token_time = None
        accumulated_text = ""
        token_count = 0

        print(f"[DEBUG] Sending streaming request to LM Studio at timestamp: {start_time}", flush=True)

        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            # Timeout set to 180 seconds for local CPU inference
            with urllib.request.urlopen(req, timeout=180.0) as response:
                for line in response:
                    line_str = line.decode("utf-8").strip()
                    if not line_str:
                        continue
                    if line_str.startswith("data: "):
                        data_payload = line_str[6:]
                        if data_payload == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_payload)
                            delta = chunk["choices"][0]["delta"]
                            if "content" in delta:
                                token = delta["content"]
                                if first_token_time is None:
                                    first_token_time = time.time()
                                    eval_time = first_token_time - start_time
                                    print(f"[DEBUG] First token received in {eval_time:.2f}s (Prompt evaluation time)", flush=True)

                                token_count += 1
                                accumulated_text += token
                                yield {"type": "token", "content": token}
                        except Exception:
                            continue

                end_time = time.time()
                total_time = end_time - start_time
                eval_time = (first_token_time - start_time) if first_token_time else total_time
                gen_time = (end_time - first_token_time) if first_token_time else 0.0
                tokens_sec = (token_count / gen_time) if gen_time > 0 else 0.0

                print(f"[DEBUG] Stream completed in {total_time:.2f}s (Eval: {eval_time:.2f}s, Gen: {gen_time:.2f}s, Speed: {tokens_sec:.1f} tokens/sec)", flush=True)

                # Parse JSON
                try:
                    data = json.loads(accumulated_text)
                    data["summary"] = data.get("reasoning", "")
                    data["findings"] = data.get("risk_drivers", []) + data.get("abnormal_vitals", []) + data.get("abnormal_labs", [])
                    data["risk"] = data.get("risk_drivers", ["Unknown"])[0] if data.get("risk_drivers") else "Unknown"
                    
                    # Attach performance metrics
                    data["performance_metrics"] = {
                        "cache": context.get("performance_metrics", {}).get("cache", "MISS") if isinstance(context, dict) else "MISS",
                        "prompt_size_chars": char_count,
                        "estimated_tokens": est_tokens,
                        "prompt_evaluation_time_ms": int(eval_time * 1000),
                        "generation_time_ms": int(gen_time * 1000),
                        "tokens_per_sec": round(tokens_sec, 1),
                        "total_response_time_ms": int(total_time * 1000)
                    }

                    print("[DEBUG] JSON parsing successful. Streaming final payload.", flush=True)
                    yield {"type": "final", "content": data}
                except Exception as json_err:
                    print("[DEBUG] JSON parsing of streaming output failed! Falling back to MockProvider for structure.", flush=True)
                    final_mock = self.mock_fallback.generate(question, context)
                    final_mock["performance_metrics"] = {
                        "cache": "MISS",
                        "prompt_size_chars": char_count,
                        "estimated_tokens": est_tokens,
                        "prompt_evaluation_time_ms": int(eval_time * 1000),
                        "generation_time_ms": int(gen_time * 1000),
                        "tokens_per_sec": round(tokens_sec, 1),
                        "total_response_time_ms": int(total_time * 1000)
                    }
                    yield {"type": "final", "content": final_mock}

        except Exception as e:
            end_time = time.time()
            elapsed = end_time - start_time
            print(f"[DEBUG] Streaming failed after {elapsed:.2f}s with exception: {e}", flush=True)
            traceback.print_exc(file=sys.stdout)
            print("[DEBUG] Falling back to MockProvider now.", flush=True)
            yield from self.mock_fallback.generate_stream(question, context)
