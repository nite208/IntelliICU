"""
app/telemetry/trend_engine.py

Enterprise Telemetry Trend Engine — Orchestrator.

This is the public facade for the entire telemetry subsystem.
External callers (simulator, API routes) interact ONLY with this class.

Responsibilities:
  - Ingest: accept a vitals dict and forward it to TelemetryStore.
  - Analyze: for one or all patients, call TrendAnalyzer per parameter
    then TrendSummarizer to build the patient summary.
  - Cache: store the most recent summary per patient so REST endpoints
    can respond instantly without re-computing.

Design for extensibility:
  - Adding a new trend type (e.g. SOFA score) requires only:
    1. Adding the parameter key to store.TRACKED_PARAMETERS.
    2. Adding a rule function to clinical_rules.RULE_REGISTRY.
    All other files remain unchanged.
"""

from __future__ import annotations

from typing import Dict, Optional

from app.telemetry.store import telemetry_store, TRACKED_PARAMETERS, TelemetryStore
from app.telemetry.trend_analyzer import trend_analyzer
from app.telemetry.trend_summary import trend_summarizer


class TelemetryEngine:
    """
    Singleton orchestrator for the telemetry trend pipeline.

    Pipeline per patient:
        ingest() → TelemetryStore.ingest()
        analyze_patient() → [TrendAnalyzer.analyze() × n_params] → TrendSummarizer.summarize()
    """

    def __init__(
        self,
        store: TelemetryStore = telemetry_store,
    ) -> None:
        self._store = store
        # Cache of most recent TrendSummary per patient.
        self._cache: Dict[str, dict] = {}
        # Patient name lookup (populated by ingest caller)
        self._patient_names: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------

    def ingest(
        self,
        patient_id: str,
        vitals: dict,
        patient_name: str = "",
    ) -> None:
        """
        Push the latest vitals into the rolling window.

        Parameters
        ----------
        patient_id : str
        vitals : dict
            Must include at minimum the keys in store.TRACKED_PARAMETERS
            (minus "map" which is computed internally).
        patient_name : str
            Optional display name stored for narrative generation.
        """
        self._store.ingest(patient_id, vitals)
        if patient_name:
            self._patient_names[patient_id] = patient_name

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze_patient(self, patient_id: str) -> dict:
        """
        Run the full trend pipeline for a single patient.

        Returns the TrendSummary dict (also stored in self._cache).
        Returns a safe empty summary if no data exists.
        """
        if not self._store.patient_has_data(patient_id, min_samples=2):
            return self._empty_summary(patient_id)

        snapshot = self._store.get_patient_snapshot(patient_id)

        per_param_results: Dict[str, dict] = {}
        for param in TRACKED_PARAMETERS:
            history = snapshot.get(param, [])
            per_param_results[param] = trend_analyzer.analyze(param, history)

        name = self._patient_names.get(patient_id, "")
        summary = trend_summarizer.summarize(patient_id, per_param_results, name)
        self._cache[patient_id] = summary
        return summary

    def analyze_all(self) -> Dict[str, dict]:
        """
        Run the pipeline for all patients currently in the store.

        Returns a dict of { patient_id: TrendSummary }.
        """
        results = {}
        for patient_id in self._store.get_all_patients():
            results[patient_id] = self.analyze_patient(patient_id)
        return results

    # ------------------------------------------------------------------
    # Cache access (for REST routes — no recomputation)
    # ------------------------------------------------------------------

    def get_cached_summary(self, patient_id: str) -> Optional[dict]:
        """Return the last computed summary without re-running the pipeline."""
        return self._cache.get(patient_id)

    def get_all_cached_summaries(self) -> Dict[str, dict]:
        """Return all cached summaries."""
        return dict(self._cache)

    def get_history_for_api(self, patient_id: str, parameter: str) -> list:
        """
        Return raw reading history for a parameter, serialisable to JSON.
        Used by the /api/telemetry/history endpoint.
        """
        history = self._store.get_history(patient_id, parameter)
        return [r.to_dict() for r in history]

    def get_all_patient_ids(self) -> list:
        return self._store.get_all_patients()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _empty_summary(self, patient_id: str) -> dict:
        return trend_summarizer.summarize(patient_id, {})

    def build_telemetry_trends_payload(self, patient_id: str) -> dict:
        """
        Return a compact per-parameter trends dict suitable for embedding
        in the existing patient WebSocket payload under "telemetry_trends".

        This is what the simulator injects into the "patient_update" message.
        """
        summary = self.analyze_patient(patient_id)
        vitals = summary.get("vitals", {})

        compact = {}
        for param, r in vitals.items():
            compact[param] = {
                "label":          r.get("label"),
                "unit":           r.get("unit"),
                "current":        r.get("current"),
                "previous":       r.get("previous"),
                "average":        r.get("average"),
                "direction":      r.get("direction"),
                "classification": r.get("classification"),
                "alert_level":    r.get("alert_level"),
                "slope":          r.get("slope"),
                "rate_of_change": r.get("rate_of_change"),
                "pct_change":     r.get("pct_change"),
                "interpretation": r.get("interpretation"),
                "deterioration_score": r.get("deterioration_score"),
                "history":        r.get("history", []),
            }

        return {
            "overall_classification": summary.get("overall_classification"),
            "overall_alert_level":    summary.get("overall_alert_level"),
            "clinical_narrative":     summary.get("clinical_narrative"),
            "combined_deterioration_score": summary.get("combined_deterioration_score"),
            "parameters":             compact,
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

telemetry_engine = TelemetryEngine()
