"""
app/services/hospital_assistant_service.py

Hospital-Wide AI Assistant Service — Phase 13.6.

Operates at the HOSPITAL level, above the per-patient ClinicalCopilotService.

Responsibilities:
  - Aggregate state from all active simulator patients.
  - Pull live telemetry trend summaries from the TelemetryEngine cache.
  - Classify each patient by severity and build a prioritized critical-patient list.
  - Answer natural-language hospital-level questions using the existing LLM factory.
  - Surface: hospital summary, critical ranking, active alerts, AI insights,
    recommended actions — all from data already produced by downstream engines.

Design rules:
  - REUSES: simulator.patients, telemetry_engine, KnowledgeService, LLM factory.
  - DOES NOT: duplicate ClinicalCopilotService logic, query DB directly for vitals
    (uses simulator state), or open new WebSockets.
  - Single Responsibility: only hospital-level aggregation and assistant chat.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional

from app.ai.mock_llm import MockClinicalLLM
from app.rag.knowledge_service import KnowledgeService
from app.telemetry.trend_engine import telemetry_engine

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Thresholds used for classification — single location, easy to tune.
# ---------------------------------------------------------------------------
_HIGH_RISK_SCORE   = 0.75
_MEDIUM_RISK_SCORE = 0.40

_CRITICAL_HR  = (50, 130)    # (low, high) — outside = abnormal
_CRITICAL_SPO2 = 90
_CRITICAL_SBP  = 90
_CRITICAL_TEMP = (35.5, 39.5)
_CRITICAL_LACT = 4.0


class HospitalAssistantService:
    """
    Hospital-wide AI clinical assistant.

    Singleton-safe — stateless apart from the KnowledgeService and LLM references.
    """

    def __init__(self) -> None:
        self.llm       = MockClinicalLLM()
        self.knowledge = KnowledgeService()
        # Conversation memory keyed by session ID ("hospital" for the default session).
        self._memory: Dict[str, List[Dict]] = {}

    # ==========================================================================
    # Patient data access — read from the already-running simulator singleton.
    # ==========================================================================

    def _get_patients(self) -> List[dict]:
        """Return the live simulator patient list (already imported globally)."""
        # Import here to avoid circular imports; simulator is a singleton so this
        # is O(1) — just a module-level attribute access.
        from app.websocket.simulator import simulator
        return list(simulator.patients)

    # ==========================================================================
    # Core Aggregation
    # ==========================================================================

    def build_hospital_snapshot(self) -> Dict[str, Any]:
        """
        Aggregate all patient state into a hospital-level snapshot.

        Returns a dict with:
          - summary            : headline KPIs
          - patients_ranked    : all patients sorted by risk descending
          - critical_patients  : patients with risk_level HIGH or risk_score >= threshold
          - active_alerts      : list of abnormal parameters per patient
          - telemetry_insights : list of patients with worsening telemetry trends
          - ai_insights        : derived textual observations
          - recommended_actions: prioritised actionable list
        """
        patients = self._get_patients()
        if not patients:
            return self._empty_snapshot()

        ranked     = sorted(patients, key=lambda p: p.get("risk_score", 0), reverse=True)
        critical   = [p for p in ranked if p.get("risk_level") == "HIGH" or p.get("risk_score", 0) >= _HIGH_RISK_SCORE]
        serious    = [p for p in ranked if p.get("risk_level") == "MEDIUM" and p not in critical]
        stable     = [p for p in ranked if p.get("risk_level") == "LOW" and p not in critical]

        total          = len(patients)
        n_critical     = len(critical)
        n_serious      = len(serious)
        n_stable       = len(stable)

        # ---- Active Alerts per patient ----
        active_alerts = []
        for p in ranked:
            flags = self._detect_abnormalities(p)
            if flags:
                active_alerts.append({
                    "patient_id":   p["id"],
                    "patient_name": p.get("name", ""),
                    "bed":          p.get("bed", ""),
                    "risk_score":   p.get("risk_score", 0),
                    "risk_level":   p.get("risk_level", "LOW"),
                    "status":       p.get("status", ""),
                    "flags":        flags,
                    "flag_count":   len(flags),
                })

        # ---- Telemetry Trend Insights ----
        telemetry_insights = self._build_telemetry_insights()

        # ---- Bed utilisation ----
        from app.websocket.simulator import simulator
        dash = simulator.dashboard
        bed_occupancy  = dash.get("bed_occupancy", 0)
        available_beds = dash.get("available_beds", 0)
        icu_capacity   = dash.get("icu_capacity", total)

        # ---- AI Insights ----
        ai_insights = self._generate_ai_insights(
            critical=critical,
            serious=serious,
            active_alerts=active_alerts,
            telemetry_insights=telemetry_insights,
            bed_occupancy=bed_occupancy,
        )

        # ---- Recommended Actions ----
        recommended_actions = self._generate_recommended_actions(critical, active_alerts, telemetry_insights)

        # ---- Summary ----
        sepsis_suspects = sum(
            1 for p in patients
            if p.get("lactate", 0) > _CRITICAL_LACT or p.get("risk_score", 0) > 0.80
        )

        summary = {
            "total_patients":       total,
            "critical_patients":    n_critical,
            "serious_patients":     n_serious,
            "stable_patients":      n_stable,
            "active_alert_count":   len(active_alerts),
            "sepsis_suspects":      sepsis_suspects,
            "bed_occupancy_pct":    bed_occupancy,
            "available_beds":       available_beds,
            "icu_capacity":         icu_capacity,
            "worsening_trend_count": len(telemetry_insights),
            "generated_at":         datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }

        return {
            "summary":             summary,
            "patients_ranked":     [self._slim_patient(p) for p in ranked],
            "critical_patients":   [self._slim_patient(p) for p in critical],
            "active_alerts":       active_alerts,
            "telemetry_insights":  telemetry_insights,
            "ai_insights":         ai_insights,
            "recommended_actions": recommended_actions,
        }

    # ==========================================================================
    # AI Chat
    # ==========================================================================

    def ask(
        self,
        question: str,
        session_id: str = "hospital",
    ) -> Dict[str, Any]:
        """
        Answer a hospital-level clinical question.

        Pipeline:
          1. Build fresh hospital snapshot.
          2. Retrieve guideline evidence from KnowledgeService.
          3. Assemble system prompt (snapshot + evidence).
          4. Call LLM factory (batch mode).
          5. Return structured response.
        """
        snapshot = self.build_hospital_snapshot()
        evidence_block, sources = self._retrieve_evidence(question)

        system_msg = self._build_system_message(snapshot, evidence_block)
        messages   = self._get_messages(session_id, system_msg, question)

        llm_context = {"conversation_history": messages, "snapshot": snapshot}
        response    = self.llm.generate_response(question, llm_context)

        # Persist assistant turn
        self._memory.setdefault(session_id, messages)
        self._memory[session_id].append({
            "role":    "assistant",
            "content": response.get("reasoning", ""),
        })
        self._prune_memory(session_id)

        return {
            **response,
            "snapshot":          snapshot,
            "retrieved_sources": sources,
        }

    def ask_stream(
        self,
        question: str,
        session_id: str = "hospital",
    ) -> Generator[str, None, None]:
        """
        Streaming hospital assistant — yields SSE-formatted JSON chunks.
        """
        snapshot = self.build_hospital_snapshot()
        evidence_block, sources = self._retrieve_evidence(question)

        system_msg = self._build_system_message(snapshot, evidence_block)
        messages   = self._get_messages(session_id, system_msg, question)

        llm_context = {"conversation_history": messages, "snapshot": snapshot}

        for chunk in self.llm.generate_stream(question, llm_context):
            if chunk["type"] == "final":
                chunk["content"]["snapshot"]          = snapshot
                chunk["content"]["retrieved_sources"] = sources

                self._memory.setdefault(session_id, messages)
                self._memory[session_id].append({
                    "role":    "assistant",
                    "content": chunk["content"].get("reasoning", ""),
                })
                self._prune_memory(session_id)

            yield f"data: {json.dumps(chunk)}\n\n"

    # ==========================================================================
    # Private helpers
    # ==========================================================================

    def _retrieve_evidence(self, question: str):
        """Search KnowledgeService — reuses the exact same pattern as ClinicalCopilotService."""
        docs = self.knowledge.search(question, top_k=3)
        if not docs:
            return "", []

        lines = ["\nRelevant Clinical Guidelines (IntelliICU Knowledge Base):"]
        sources = []
        for doc in docs:
            lines.append(
                f"\n- Title: {doc['title']}\n"
                f"  Source: {doc['source']}\n"
                f"  Content: {doc['content']}"
            )
            sources.append({
                "id":               doc["id"],
                "title":            doc["title"],
                "source":           doc["source"],
                "category":         doc["category"],
                "section":          doc["section"],
                "similarity_score": doc.get("score", 0.0),
            })
        return "\n".join(lines), sources

    def _build_system_message(self, snapshot: dict, evidence_block: str) -> str:
        """Build the system prompt from the hospital snapshot + evidence."""
        summary   = snapshot.get("summary", {})
        critical  = snapshot.get("critical_patients", [])
        alerts    = snapshot.get("active_alerts", [])
        insights  = snapshot.get("ai_insights", [])

        critical_text = "\n".join(
            f"  • {p['name']} ({p['id']}) Bed {p['bed']} — Risk {int(p['risk_score']*100)}% — Status: {p['status']}"
            for p in critical[:5]
        ) or "  None"

        alert_text = "\n".join(
            f"  • {a['patient_name']} ({a['patient_id']}): {', '.join(a['flags'][:3])}"
            for a in alerts[:5]
        ) or "  None"

        return (
            "You are an enterprise-grade hospital-wide ICU AI Clinical Assistant. "
            "You have access to real-time data for all active ICU patients. "
            "Answer the clinical question with precision, citing specific patient data when relevant.\n\n"
            f"=== HOSPITAL STATUS (as of {summary.get('generated_at', 'now')}) ===\n"
            f"Total ICU Patients: {summary.get('total_patients')}\n"
            f"Critical: {summary.get('critical_patients')}  "
            f"Serious: {summary.get('serious_patients')}  "
            f"Stable: {summary.get('stable_patients')}\n"
            f"Active Alerts: {summary.get('active_alert_count')}\n"
            f"Bed Occupancy: {summary.get('bed_occupancy_pct')}%  "
            f"Available: {summary.get('available_beds')}/{summary.get('icu_capacity')}\n"
            f"Sepsis Suspects: {summary.get('sepsis_suspects')}\n"
            f"Worsening Trends: {summary.get('worsening_trend_count')}\n\n"
            f"=== CRITICAL PATIENTS ===\n{critical_text}\n\n"
            f"=== ACTIVE ALERTS ===\n{alert_text}\n\n"
            f"=== AI INSIGHTS ===\n"
            + "\n".join(f"  • {i}" for i in insights[:4])
            + (evidence_block or "")
        )

    def _get_messages(
        self, session_id: str, system_msg: str, question: str
    ) -> List[Dict]:
        """Build or update the conversation message list for this session."""
        if session_id not in self._memory:
            self._memory[session_id] = [{"role": "system", "content": system_msg}]
        else:
            # Refresh system message with latest snapshot
            self._memory[session_id][0] = {"role": "system", "content": system_msg}

        self._memory[session_id].append({"role": "user", "content": question})
        return self._memory[session_id]

    def _prune_memory(self, session_id: str, max_turns: int = 8) -> None:
        history = self._memory.get(session_id, [])
        if len(history) > max_turns + 1:
            self._memory[session_id] = [history[0]] + history[-(max_turns):]

    def _slim_patient(self, p: dict) -> dict:
        """Return a small patient summary dict for API responses."""
        return {
            "id":          p["id"],
            "name":        p.get("name", ""),
            "age":         p.get("age"),
            "gender":      p.get("gender", ""),
            "bed":         p.get("bed", ""),
            "status":      p.get("status", ""),
            "risk_level":  p.get("risk_level", "LOW"),
            "risk_score":  round(p.get("risk_score", 0), 3),
            "heart_rate":  p.get("heart_rate"),
            "spo2":        p.get("spo2"),
            "systolic_bp": p.get("systolic_bp"),
            "temperature": p.get("temperature"),
            "lactate":     p.get("lactate"),
        }

    def _detect_abnormalities(self, p: dict) -> List[str]:
        """Return a list of clinical alert strings for a single patient."""
        flags = []
        hr   = p.get("heart_rate", 0)
        spo2 = p.get("spo2", 100)
        sbp  = p.get("systolic_bp", 120)
        temp = p.get("temperature", 37)
        lact = p.get("lactate", 1)
        rr   = p.get("respiratory_rate", 16)

        if hr > _CRITICAL_HR[1]:
            flags.append(f"Tachycardia HR {hr} bpm")
        elif hr < _CRITICAL_HR[0]:
            flags.append(f"Bradycardia HR {hr} bpm")
        if spo2 < _CRITICAL_SPO2:
            flags.append(f"Hypoxia SpO\u2082 {spo2}%")
        if sbp < _CRITICAL_SBP:
            flags.append(f"Hypotension SBP {sbp} mmHg")
        if temp > _CRITICAL_TEMP[1]:
            flags.append(f"Hyperpyrexia {temp}\u00b0C")
        elif temp < _CRITICAL_TEMP[0]:
            flags.append(f"Hypothermia {temp}\u00b0C")
        if lact > _CRITICAL_LACT:
            flags.append(f"Hyperlactataemia {lact} mmol/L")
        if rr > 28:
            flags.append(f"Severe tachypnoea RR {rr}/min")
        if p.get("risk_score", 0) >= _HIGH_RISK_SCORE:
            flags.append(f"High AI risk score {int(p['risk_score']*100)}%")
        return flags

    def _build_telemetry_insights(self) -> List[dict]:
        """
        Pull worsening-trend summaries from the TelemetryEngine cache.
        Returns patients with overall_alert_level WARNING or CRITICAL.
        """
        insights = []
        for pid in telemetry_engine.get_all_patient_ids():
            cached = telemetry_engine.get_cached_summary(pid)
            if not cached:
                continue
            al = cached.get("overall_alert_level", "NORMAL")
            if al in ("WARNING", "CRITICAL"):
                insights.append({
                    "patient_id":            pid,
                    "patient_name":          cached.get("patient_name", ""),
                    "overall_alert_level":   al,
                    "overall_classification": cached.get("overall_classification"),
                    "clinical_narrative":    cached.get("clinical_narrative", ""),
                    "deterioration_score":   cached.get("combined_deterioration_score", 0),
                    "critical_parameters":   [
                        c["label"] for c in cached.get("critical_parameters", [])[:3]
                    ],
                })
        insights.sort(key=lambda x: x.get("deterioration_score", 0), reverse=True)
        return insights

    def _generate_ai_insights(
        self,
        critical: List[dict],
        serious: List[dict],
        active_alerts: List[dict],
        telemetry_insights: List[dict],
        bed_occupancy: float,
    ) -> List[str]:
        """Generate deterministic AI insight strings from aggregated data."""
        insights = []

        if critical:
            top = critical[0]
            insights.append(
                f"{top.get('name', top['id'])} (Bed {top.get('bed')}) is the highest-risk patient "
                f"with AI risk score {int(top.get('risk_score', 0)*100)}%."
            )

        sepsis_risk = [p for p in critical if p.get("lactate", 0) > 2.5]
        if sepsis_risk:
            names = ", ".join(p.get("name", p["id"]) for p in sepsis_risk[:3])
            insights.append(
                f"{len(sepsis_risk)} patient(s) show elevated lactate consistent with sepsis: {names}."
            )

        if telemetry_insights:
            top_ti = telemetry_insights[0]
            insights.append(
                f"Telemetry trend alert: {top_ti['patient_name'] or top_ti['patient_id']} — "
                f"{top_ti['clinical_narrative']}"
            )

        if bed_occupancy > 90:
            insights.append(
                f"ICU bed occupancy is critically high at {bed_occupancy:.1f}%. "
                "Consider capacity escalation protocol."
            )
        elif bed_occupancy > 80:
            insights.append(f"ICU bed occupancy is elevated at {bed_occupancy:.1f}%.")

        multi_alert = [a for a in active_alerts if a["flag_count"] >= 3]
        if multi_alert:
            names = ", ".join(a["patient_name"] for a in multi_alert[:2])
            insights.append(
                f"{len(multi_alert)} patient(s) have 3+ concurrent abnormal parameters: {names}."
            )

        if not insights:
            insights.append("All ICU patients are within monitored parameters. Continue routine surveillance.")

        return insights

    def _generate_recommended_actions(
        self,
        critical: List[dict],
        active_alerts: List[dict],
        telemetry_insights: List[dict],
    ) -> List[dict]:
        """Generate prioritised actionable recommendations."""
        actions = []

        # Highest-risk patients
        for p in critical[:3]:
            actions.append({
                "priority":    "URGENT",
                "patient_id":  p["id"],
                "patient_name": p.get("name", ""),
                "action":      f"Immediate physician review — risk score {int(p.get('risk_score',0)*100)}%",
                "rationale":   f"Status: {p.get('status')}, Bed: {p.get('bed')}",
            })

        # Active alerts — multi-flag patients
        for alert in active_alerts:
            if alert["flag_count"] >= 2:
                actions.append({
                    "priority":    "HIGH",
                    "patient_id":  alert["patient_id"],
                    "patient_name": alert["patient_name"],
                    "action":      f"Assess {', '.join(alert['flags'][:2])}",
                    "rationale":   f"{alert['flag_count']} abnormal parameters detected",
                })
                if len(actions) >= 8:
                    break

        # Worsening telemetry
        for ti in telemetry_insights[:2]:
            actions.append({
                "priority":    "HIGH",
                "patient_id":  ti["patient_id"],
                "patient_name": ti.get("patient_name", ""),
                "action":      f"Review worsening telemetry trend — {', '.join(ti.get('critical_parameters', [])[:2])}",
                "rationale":   ti.get("clinical_narrative", ""),
            })

        # Deduplicate by patient_id (keep first/highest priority)
        seen     = set()
        deduped  = []
        priority_order = {"URGENT": 0, "HIGH": 1, "MEDIUM": 2}
        actions.sort(key=lambda a: priority_order.get(a["priority"], 9))
        for a in actions:
            if a["patient_id"] not in seen:
                deduped.append(a)
                seen.add(a["patient_id"])

        return deduped

    def _empty_snapshot(self) -> dict:
        return {
            "summary":             {"total_patients": 0, "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")},
            "patients_ranked":     [],
            "critical_patients":   [],
            "active_alerts":       [],
            "telemetry_insights":  [],
            "ai_insights":         ["Awaiting patient data from simulator."],
            "recommended_actions": [],
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
hospital_assistant = HospitalAssistantService()
