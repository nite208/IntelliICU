"""
Clinical Copilot Service.

Unified reasoning pipeline (Phase 12.3):
    Question
      -> KnowledgeService.search(top_k=3)   [evidence retrieval]
      -> Patient Context (cached + optimized)
      -> LLM Provider (streaming or batch)
      -> Structured Response  { ...fields..., retrieved_sources: [...] }

ClinicalRAGService keyword-routing has been removed.
All questions now follow the same path regardless of topic.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Generator, List, Tuple

from app.services.context_builder import PatientContextBuilder
from app.services.context_optimizer import ContextOptimizer
from app.ai.mock_llm import MockClinicalLLM
from app.rag.knowledge_service import KnowledgeService
from app.clinical_reasoning.differential_engine import DifferentialEngine
from app.clinical_reasoning.treatment_engine import TreatmentEngine
from app.clinical_reasoning.medication_engine import MedicationEngine
from app.clinical_reasoning.risk_score_engine import RiskScoreEngine
from app.clinical_reasoning.laboratory_engine import LaboratoryEngine
from app.clinical_reasoning.trend_engine import TrendEngine

logger = logging.getLogger(__name__)


class ClinicalCopilotService:
    """
    Business logic layer for Clinical Copilot interactions.

    Responsibilities
    ----------------
    - Optimise and cache patient context per telemetry checksum.
    - Retrieve relevant clinical evidence via KnowledgeService.
    - Maintain per-patient conversation history (last 4 exchanges).
    - Route every query through a single LLM pipeline.
    - Return structured responses with retrieved_sources metadata.
    """

    def __init__(self):
        self.context_builder = PatientContextBuilder()
        self.llm             = MockClinicalLLM()
        self.knowledge       = KnowledgeService()

        # Configuration
        self.max_tokens = int(os.getenv("CLINICAL_LLM_MAX_TOKENS", 400))

        # In-memory session caches
        self.context_cache      = {}   # patient_id -> {"optimized": dict, "checksum": tuple}
        self.conversation_memory = {}  # patient_id -> list[message turns]

    # ------------------------------------------------------------------
    # Telemetry checksum
    # ------------------------------------------------------------------

    def _get_telemetry_checksum(self, context: Dict[str, Any]) -> tuple:
        """
        Lightweight fingerprint of the vitals/labs/alerts state.
        Used to decide whether the cached optimized context is still valid.
        """
        vitals = context.get("vitals", {}) or {}
        labs   = context.get("labs",   {}) or {}
        alerts = context.get("alerts", []) or []
        return (
            vitals.get("heart_rate"),
            vitals.get("spo2"),
            vitals.get("temperature"),
            vitals.get("systolic_bp"),
            vitals.get("diastolic_bp"),
            vitals.get("respiratory_rate"),
            labs.get("lactate"),
            labs.get("wbc"),
            len(alerts),
        )

    # ------------------------------------------------------------------
    # Evidence retrieval
    # ------------------------------------------------------------------

    def _build_evidence_block(self, question: str) -> Tuple[str, List[Dict], List[Dict]]:
        """
        Search the KnowledgeService for the top-3 documents relevant to ``question``.

        Returns
        -------
        evidence_text : str
            Formatted block ready for the system prompt; empty string when nothing found.
        retrieved_sources : list[dict]
            Slim metadata (id, title, source, category, section, similarity_score) for the API response.
        evidence_used : list[dict]
            Semantic evidence details (title, organization, section, semantic_score) for the API response.
        """
        docs = self.knowledge.search(question, top_k=3)
        if not docs:
            return "", [], []

        lines = ["\nClinical Evidence (retrieved from IntelliICU Knowledge Base):"]
        sources: List[Dict] = []
        evidence_used: List[Dict] = []
        for doc in docs:
            lines.append(
                f"\n- Title   : {doc['title']}\n"
                f"  Source  : {doc['source']}\n"
                f"  Section : {doc['section']}\n"
                f"  Content : {doc['content']}"
            )
            sources.append({
                "id":               doc["id"],
                "title":            doc["title"],
                "source":           doc["source"],
                "category":         doc["category"],
                "section":          doc["section"],
                "similarity_score": doc.get("score", 0.0),
            })
            evidence_used.append({
                "title":            doc["title"],
                "organization":     doc["source"],
                "section":          doc["section"],
                "semantic_score":   doc.get("score", 0.0),
            })

        logger.info(
            "[KnowledgeService] Retrieved %d evidence document(s) for: %r",
            len(docs), question,
        )
        return "\n".join(lines), sources, evidence_used

    # ------------------------------------------------------------------
    # Context + conversation memory resolver
    # ------------------------------------------------------------------

    def _resolve_context_and_memory(
        self, patient_id: str, question: str
    ) -> Tuple[Dict, Dict, List[Dict], List[Dict]]:
        """
        1. Build (or retrieve from cache) the optimised patient context.
        2. Retrieve relevant clinical evidence for ``question``.
        3. Assemble the system message with both patient context and evidence.
        4. Append the user turn to conversation memory.
        5. Prune memory to ≤ 4 full exchanges (system + 8 turns).

        Returns
        -------
        full_context      : raw full patient context dict (for UI rendering)
        llm_context       : dict passed to the LLM provider
        retrieved_sources : evidence metadata for the API response
        evidence_used     : detailed citation structures for the API response
        """
        # ── 1. Patient context (cached) ──────────────────────────────────
        full_context = self.context_builder.build_context(patient_id)
        checksum     = self._get_telemetry_checksum(full_context)

        t0 = time.time()
        if (
            patient_id in self.context_cache
            and self.context_cache[patient_id]["checksum"] == checksum
        ):
            cache_status      = "HIT"
            optimized_context = self.context_cache[patient_id]["optimized"]
        else:
            cache_status      = "MISS"
            optimized_context = ContextOptimizer.optimize(full_context)
            self.context_cache[patient_id] = {
                "optimized": optimized_context,
                "checksum":  checksum,
            }
        build_time_ms = int((time.time() - t0) * 1000)

        # ── 2. Evidence retrieval ────────────────────────────────────────
        evidence_text, retrieved_sources, evidence_used = self._build_evidence_block(question)

        # ── 3. System message ────────────────────────────────────────────
        system_instruction = (
            "You are an expert ICU Clinical Decision Support AI. "
            "Analyze the provided patient context and answer the clinical question.\n"
            f"Patient Context Summary:\n{json.dumps(optimized_context, indent=2)}"
            + evidence_text
        )

        # ── 4. Conversation memory ───────────────────────────────────────
        if patient_id not in self.conversation_memory:
            self.conversation_memory[patient_id] = [
                {"role": "system", "content": system_instruction}
            ]
        else:
            if cache_status == "MISS":
                # Sync system message when context has changed
                self.conversation_memory[patient_id][0] = {
                    "role": "system", "content": system_instruction
                }

        self.conversation_memory[patient_id].append(
            {"role": "user", "content": question}
        )

        # ── 5. Prune to ≤ system + 8 turns ──────────────────────────────
        history = self.conversation_memory[patient_id]
        if len(history) > 9:
            self.conversation_memory[patient_id] = [history[0]] + history[-8:]

        # ── 6. LLM context payload ───────────────────────────────────────
        llm_context = {
            "conversation_history": self.conversation_memory[patient_id],
            "performance_metrics": {
                "cache":                cache_status,
                "max_tokens":           self.max_tokens,
                "context_build_time_ms": build_time_ms,
            },
        }

        return full_context, llm_context, retrieved_sources, evidence_used

    def _extract_abnormalities(self, context: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        Helper to extract abnormal vitals and labs from the patient context
        consistent with the ExplainableReasoningService rules.
        """
        vitals = context.get("vitals") or {}
        hr = vitals.get("heart_rate")
        spo2 = vitals.get("spo2")
        temp = vitals.get("temperature")
        sys_bp = vitals.get("systolic_bp")
        dia_bp = vitals.get("diastolic_bp")

        abnormal_vitals = []
        if hr and hr > 100:
            abnormal_vitals.append(f"Tachycardia (HR: {hr} bpm)")
        if spo2 and spo2 < 92:
            abnormal_vitals.append(f"Hypoxemia (SpO2: {spo2}%)")
        if temp and temp >= 38.0:
            abnormal_vitals.append(f"Fever (Temp: {temp}°C)")
        elif temp and temp < 36.0:
            abnormal_vitals.append(f"Hypothermia (Temp: {temp}°C)")
        if sys_bp and sys_bp < 90:
            abnormal_vitals.append(f"Hypotension (BP: {sys_bp}/{dia_bp} mmHg)")

        trends = context.get("vital_trends") or {}
        for metric, info in trends.items():
            if isinstance(info, dict) and info.get("direction") in ["rising", "falling"]:
                abnormal_vitals.append(f"Trend: {metric} is {info['direction']}")

        abnormal_labs = []
        for lab in context.get("abnormal_labs", []):
            abnormal_labs.append(f"{lab['metric']}: {lab['value']} ({lab['severity']})")

        return abnormal_vitals, abnormal_labs

    # ------------------------------------------------------------------
    # Public API – batch
    # ------------------------------------------------------------------

    def get_answer(self, patient_id: str, question: str) -> Dict[str, Any]:
        """
        Unified batch inference:
            KnowledgeService → patient context → LLM → structured response
        """
        context, llm_context, retrieved_sources, evidence_used = self._resolve_context_and_memory(
            patient_id, question
        )

        response = self.llm.generate_response(question, llm_context)
        response["context"]           = context
        response["retrieved_sources"] = retrieved_sources
        response["evidence_used"]     = evidence_used

        # Run differential diagnosis engine
        abnormal_vitals, abnormal_labs = self._extract_abnormalities(context)
        admission = context.get("admission", {}) or {}
        diagnosis = admission.get("diagnosis", "")
        response["differential_diagnosis"] = DifferentialEngine.evaluate(
            context=context,
            abnormal_vitals=abnormal_vitals,
            abnormal_labs=abnormal_labs,
            admission_diagnosis=diagnosis,
            retrieved_sources=retrieved_sources
        )

        # Run treatment pathway engine
        vitals = context.get("vitals", {}) or {}
        labs = context.get("labs", {}) or {}
        response["treatment_pathway"] = TreatmentEngine.generate(
            differential_diagnosis=response["differential_diagnosis"],
            context=context,
            vitals=vitals,
            labs=labs,
            retrieved_sources=retrieved_sources
        )

        # Run medication recommendation engine
        response["medication_plan"] = MedicationEngine.generate(
            treatment_pathway=response["treatment_pathway"],
            differential_diagnosis=response["differential_diagnosis"],
            context=context,
            vitals=vitals,
            labs=labs,
            drug_rag_results=retrieved_sources
        )

        # Run clinical risk score engine
        gcs_val = context.get("patient", {}).get("gcs") or context.get("labs", {}).get("gcs") or 15
        response["risk_scores"] = RiskScoreEngine.calculate(
            vitals=vitals,
            labs=labs,
            gcs=gcs_val,
            context=context
        )

        # Run laboratory interpretation engine
        response["laboratory_interpretation"] = LaboratoryEngine.generate(
            context=context
        )

        # Run clinical trend engine
        response["trend_analysis"] = TrendEngine.generate(
            context=context
        )

        # Record assistant turn for follow-up memory
        self.conversation_memory[patient_id].append({
            "role":    "assistant",
            "content": response.get("reasoning", ""),
        })

        return response

    # ------------------------------------------------------------------
    # Public API – streaming
    # ------------------------------------------------------------------

    def get_streaming_answer(
        self, patient_id: str, question: str
    ) -> Generator[str, None, None]:
        """
        Unified streaming inference via Server-Sent Events (SSE):
            KnowledgeService → patient context → LLM stream → SSE chunks
        """
        context, llm_context, retrieved_sources, evidence_used = self._resolve_context_and_memory(
            patient_id, question
        )

        for chunk in self.llm.generate_stream(question, llm_context):
            if chunk["type"] == "final":
                chunk["content"]["context"]           = context
                chunk["content"]["retrieved_sources"] = retrieved_sources
                chunk["content"]["evidence_used"]     = evidence_used

                # Run differential diagnosis engine
                abnormal_vitals, abnormal_labs = self._extract_abnormalities(context)
                admission = context.get("admission", {}) or {}
                diagnosis = admission.get("diagnosis", "")
                chunk["content"]["differential_diagnosis"] = DifferentialEngine.evaluate(
                    context=context,
                    abnormal_vitals=abnormal_vitals,
                    abnormal_labs=abnormal_labs,
                    admission_diagnosis=diagnosis,
                    retrieved_sources=retrieved_sources
                )

                # Run treatment pathway engine
                vitals = context.get("vitals", {}) or {}
                labs = context.get("labs", {}) or {}
                chunk["content"]["treatment_pathway"] = TreatmentEngine.generate(
                    differential_diagnosis=chunk["content"]["differential_diagnosis"],
                    context=context,
                    vitals=vitals,
                    labs=labs,
                    retrieved_sources=retrieved_sources
                )

                # Run medication recommendation engine
                chunk["content"]["medication_plan"] = MedicationEngine.generate(
                    treatment_pathway=chunk["content"]["treatment_pathway"],
                    differential_diagnosis=chunk["content"]["differential_diagnosis"],
                    context=context,
                    vitals=vitals,
                    labs=labs,
                    drug_rag_results=retrieved_sources
                )

                # Run clinical risk score engine
                gcs_val = context.get("patient", {}).get("gcs") or context.get("labs", {}).get("gcs") or 15
                chunk["content"]["risk_scores"] = RiskScoreEngine.calculate(
                    vitals=vitals,
                    labs=labs,
                    gcs=gcs_val,
                    context=context
                )

                # Run laboratory interpretation engine
                chunk["content"]["laboratory_interpretation"] = LaboratoryEngine.generate(
                    context=context
                )

                # Run clinical trend engine
                chunk["content"]["trend_analysis"] = TrendEngine.generate(
                    context=context
                )

                # Record assistant turn for follow-up memory
                self.conversation_memory[patient_id].append({
                    "role":    "assistant",
                    "content": chunk["content"].get("reasoning", ""),
                })

            yield f"data: {json.dumps(chunk)}\n\n"
