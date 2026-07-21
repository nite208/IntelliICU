"""
app/telemetry/trend_summary.py

Patient-Level Trend Summarizer.

Responsibilities:
  - Accept a dict of per-parameter TrendResult dicts (from TrendAnalyzer).
  - Compute the worst-case classification and alert level across all parameters.
  - Build a chronological timeline of significant trend changes.
  - Generate a concise, physician-grade clinical narrative string.

This module contains no I/O, no DB access, and no math — only aggregation and
natural-language generation from pre-computed per-parameter data.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from app.telemetry.clinical_rules import ALERT_SEVERITY, CLASSIFICATION_SEVERITY


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _direction_arrow(direction: str) -> str:
    """Return a unicode arrow for the given direction string."""
    return {
        "RISING":      "\u2191",   # ↑
        "FALLING":     "\u2193",   # ↓
        "STABLE":      "\u2192",   # →
        "OSCILLATING": "\u2248",   # ≈
        "SPIKE_UP":    "\u21d1",   # ⇑
        "SPIKE_DOWN":  "\u21d3",   # ⇓
    }.get(direction, "\u2192")


def _alert_color(alert_level: str) -> str:
    """Map alert level to a frontend colour token."""
    return {
        "NORMAL":   "green",
        "WATCH":    "yellow",
        "WARNING":  "orange",
        "CRITICAL": "red",
    }.get(alert_level, "gray")


# ---------------------------------------------------------------------------
# Summarizer
# ---------------------------------------------------------------------------

class TrendSummarizer:
    """
    Synthesises per-parameter TrendResult dicts into a patient-level summary.
    """

    def summarize(
        self,
        patient_id: str,
        results: Dict[str, dict],
        patient_name: str = "",
    ) -> dict:
        """
        Build the complete patient trend summary.

        Parameters
        ----------
        patient_id : str
        results : dict[parameter, TrendResult]
        patient_name : str
            Optional — included in the narrative.

        Returns
        -------
        A TrendSummary dict ready for JSON serialisation.
        """
        if not results:
            return self._empty_summary(patient_id)

        # ------------------------------------------------------------------
        # 1. Worst-case classification and alert level
        # ------------------------------------------------------------------
        overall_alert = "NORMAL"
        overall_class = "Stable"

        for param, r in results.items():
            al = r.get("alert_level", "NORMAL")
            cl = r.get("classification", "Stable")
            if ALERT_SEVERITY.get(al, 0) > ALERT_SEVERITY.get(overall_alert, 0):
                overall_alert = al
            if CLASSIFICATION_SEVERITY.get(cl, 0) > CLASSIFICATION_SEVERITY.get(overall_class, 0):
                overall_class = cl

        # ------------------------------------------------------------------
        # 2. Categorise parameters by alert level
        # ------------------------------------------------------------------
        critical_params  = []
        warning_params   = []
        watch_params     = []
        normal_params    = []
        improving_params = []

        for param, r in results.items():
            al = r.get("alert_level", "NORMAL")
            cl = r.get("classification", "Stable")
            entry = {
                "parameter":      param,
                "label":          r.get("label", param),
                "abbrev":         r.get("abbrev", param),
                "unit":           r.get("unit", ""),
                "current":        r.get("current"),
                "direction":      r.get("direction", "STABLE"),
                "arrow":          _direction_arrow(r.get("direction", "STABLE")),
                "alert_level":    al,
                "alert_color":    _alert_color(al),
                "classification": cl,
                "pct_change":     r.get("pct_change", 0.0),
                "interpretation": r.get("interpretation", ""),
            }
            if cl == "Improving":
                improving_params.append(entry)
            elif al == "CRITICAL":
                critical_params.append(entry)
            elif al == "WARNING":
                warning_params.append(entry)
            elif al == "WATCH":
                watch_params.append(entry)
            else:
                normal_params.append(entry)

        # ------------------------------------------------------------------
        # 3. Timeline — last meaningful direction changes across all params
        # ------------------------------------------------------------------
        timeline = self._build_timeline(results)

        # ------------------------------------------------------------------
        # 4. Clinical narrative
        # ------------------------------------------------------------------
        narrative = self._generate_narrative(results, overall_class, overall_alert)

        # ------------------------------------------------------------------
        # 5. Combined early deterioration score (max across parameters)
        # ------------------------------------------------------------------
        combined_det_score = max(
            (r.get("deterioration_score", 0.0) for r in results.values()),
            default=0.0,
        )

        return {
            "patient_id":            patient_id,
            "patient_name":          patient_name,
            "timestamp":             datetime.utcnow().strftime("%H:%M:%S"),
            "overall_classification": overall_class,
            "overall_alert_level":   overall_alert,
            "alert_color":           _alert_color(overall_alert),
            "combined_deterioration_score": round(combined_det_score, 3),
            "clinical_narrative":    narrative,
            "critical_parameters":   critical_params,
            "warning_parameters":    warning_params,
            "watch_parameters":      watch_params,
            "normal_parameters":     normal_params,
            "improving_parameters":  improving_params,
            "timeline":              timeline,
            "vitals":                results,  # full per-parameter results
        }

    # ------------------------------------------------------------------
    # Timeline builder
    # ------------------------------------------------------------------

    def _build_timeline(self, results: Dict[str, dict]) -> List[dict]:
        """
        Build a list of timeline events, one entry per parameter that is NOT
        stable-normal.  Sorted: CRITICAL first, then WARNING, then WATCH,
        then Improving, then Stable.
        """
        events = []
        now_str = datetime.utcnow().strftime("%H:%M:%S")

        for param, r in results.items():
            al = r.get("alert_level", "NORMAL")
            cl = r.get("classification", "Stable")
            direction = r.get("direction", "STABLE")
            current = r.get("current")
            unit = r.get("unit", "")
            label = r.get("label", param)
            arrow = _direction_arrow(direction)

            events.append({
                "time":           now_str,
                "parameter":      param,
                "label":          label,
                "direction":      direction,
                "arrow":          arrow,
                "classification": cl,
                "alert_level":    al,
                "alert_color":    _alert_color(al),
                "value":          current,
                "unit":           unit,
                "summary":        f"{label} {arrow} {current} {unit}".strip(),
                "_severity":      ALERT_SEVERITY.get(al, 0),
            })

        # Sort: highest severity first, then alphabetically
        events.sort(key=lambda e: (-e["_severity"], e["label"]))
        for e in events:
            del e["_severity"]

        return events

    # ------------------------------------------------------------------
    # Narrative generator
    # ------------------------------------------------------------------

    def _generate_narrative(
        self,
        results: Dict[str, dict],
        overall_class: str,
        overall_alert: str,
    ) -> str:
        """
        Generate a physician-grade clinical summary narrative.

        Rules:
          - List the 2–3 most alarming parameters.
          - Quantify changes with absolute values and direction.
          - End with a combined clinical interpretation.
        """
        # Collect alarming parameters (WARNING or CRITICAL)
        alarming = [
            r for r in results.values()
            if r.get("alert_level") in ("WARNING", "CRITICAL")
        ]
        # Sort by deterioration score descending
        alarming.sort(key=lambda r: r.get("deterioration_score", 0.0), reverse=True)

        if not alarming:
            # Check for WATCH
            watching = [r for r in results.values() if r.get("alert_level") == "WATCH"]
            if watching:
                labels = ", ".join(r.get("label", "") for r in watching[:3])
                return (
                    f"Vital signs are generally within acceptable limits. "
                    f"{labels} warrant close observation."
                )
            return (
                "All monitored telemetry parameters are within normal ranges. "
                "Haemodynamic status appears stable."
            )

        segments = []
        for r in alarming[:3]:
            label = r.get("label", "")
            cur   = r.get("current")
            prev  = r.get("previous")
            unit  = r.get("unit", "")
            arrow = _direction_arrow(r.get("direction", "STABLE"))
            pct   = r.get("pct_change", 0.0)

            if cur is not None and prev is not None and cur != prev:
                diff = abs(round(cur - prev, 1))
                direction_word = "increased" if cur > prev else "decreased"
                segments.append(
                    f"{label} has {direction_word} from {prev:.0f} to {cur:.0f} {unit} "
                    f"({arrow} {pct:+.1f}%)"
                )
            elif cur is not None:
                segments.append(f"{label} is {cur:.0f} {unit} {arrow}")

        if not segments:
            return "Trend analysis in progress — insufficient data for narrative."

        body = "; ".join(segments) + "."

        # Clinical conclusion
        if overall_alert == "CRITICAL":
            conclusion = (
                " Combined findings indicate immediate clinical deterioration — "
                "urgent physician assessment required."
            )
        elif overall_alert == "WARNING":
            conclusion = (
                " Combined trend suggests evolving haemodynamic instability — "
                "clinical review recommended."
            )
        else:
            conclusion = (
                " Continue close monitoring and reassess at next clinical interval."
            )

        return body + conclusion

    # ------------------------------------------------------------------

    def _empty_summary(self, patient_id: str) -> dict:
        return {
            "patient_id":                patient_id,
            "patient_name":              "",
            "timestamp":                 datetime.utcnow().strftime("%H:%M:%S"),
            "overall_classification":    "Unknown",
            "overall_alert_level":       "WATCH",
            "alert_color":               "gray",
            "combined_deterioration_score": 0.0,
            "clinical_narrative":        "Collecting telemetry samples — trend analysis pending.",
            "critical_parameters":       [],
            "warning_parameters":        [],
            "watch_parameters":          [],
            "normal_parameters":         [],
            "improving_parameters":      [],
            "timeline":                  [],
            "vitals":                    {},
        }


# Module-level singleton
trend_summarizer = TrendSummarizer()
