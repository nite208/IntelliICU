"""
app/telemetry/trend_analyzer.py

Per-Parameter Telemetry Trend Analyzer.

Responsibilities:
  - Accept raw TelemetryReading history for a single parameter.
  - Compute all statistical metrics (slope, std, median, variability, etc.)
    using the pure utility functions in utils.py.
  - Apply clinical rules from clinical_rules.py to classify the trend.
  - Return a fully populated TrendResult dict.

This module contains no I/O, no database access, and no clinical domain logic.
Clinical knowledge lives exclusively in clinical_rules.py.
"""

from __future__ import annotations

from typing import List, Dict, Optional

from app.telemetry.store import (
    TelemetryReading,
    PARAMETER_META,
    NORMAL_RANGES,
)
from app.telemetry import utils as U
from app.telemetry.clinical_rules import classify_parameter


# Minimum number of readings required to produce a trend result.
# With < MIN_SAMPLES we return an "Unknown" placeholder.
MIN_SAMPLES: int = 2


class TrendAnalyzer:
    """
    Stateless per-parameter trend analyzer.

    Usage::

        analyzer = TrendAnalyzer()
        result = analyzer.analyze("heart_rate", history)
    """

    def analyze(
        self,
        parameter: str,
        history: List[TelemetryReading],
    ) -> dict:
        """
        Analyze a list of TelemetryReading objects for `parameter`.

        Parameters
        ----------
        parameter : str
            One of TRACKED_PARAMETERS (e.g. "heart_rate", "map").
        history : list[TelemetryReading]
            Ordered oldest → newest.

        Returns
        -------
        dict
            A fully populated TrendResult dict.
        """
        meta = PARAMETER_META.get(parameter, {"label": parameter, "unit": "", "abbrev": parameter})
        normal = NORMAL_RANGES.get(parameter, (0.0, float("inf")))

        # --- Insufficient data ---
        if len(history) < MIN_SAMPLES:
            return self._unknown_result(parameter, meta, history)

        values = [r.value for r in history]

        # ---------- Core Statistics ----------
        current     = values[-1]
        previous    = values[-2]
        avg         = U.compute_mean(values)
        median_v    = U.compute_median(values)
        std_v       = U.compute_std(values)
        min_v       = U.compute_min(values)
        max_v       = U.compute_max(values)
        slope       = U.compute_slope(values)
        rate_chg    = U.compute_rate_of_change(current, previous)
        pct_chg     = U.compute_pct_change(current, previous)
        confidence  = U.compute_trend_confidence(values, slope)
        variability = U.compute_variability_score(values)

        # ---------- Pattern Detection ----------
        spike_flag, spike_dir = U.detect_spike(values)
        oscillating = U.detect_oscillation(values)
        persistent_rise = U.detect_persistent_trend(values, "UP")
        persistent_fall = U.detect_persistent_trend(values, "DOWN")

        # ---------- Abnormality Counters ----------
        low_n, high_n = normal
        consec_abnormal = U.count_consecutive_abnormal(values, low_n, high_n)
        time_abnormal   = U.compute_time_abnormal_pct(values, low_n, high_n)

        # ---------- Trend Direction ----------
        if spike_flag:
            direction = f"SPIKE_{spike_dir}"
        elif oscillating:
            direction = "OSCILLATING"
        elif abs(slope) < 0.05:
            direction = "STABLE"
        elif slope > 0:
            direction = "RISING"
        else:
            direction = "FALLING"

        # ---------- Early Deterioration Score ----------
        # "deteriorating direction" means moving further from normal.
        is_worsening_dir = not _moving_toward_normal(slope, current, low_n, high_n)
        det_score = U.compute_early_deterioration_score(
            slope, pct_chg, consec_abnormal, time_abnormal, is_worsening_dir
        )

        # ---------- Clinical Classification ----------
        trend_profile = {
            "current":              current,
            "previous":             previous,
            "average":              avg,
            "slope":                slope,
            "pct_change":           pct_chg,
            "std":                  std_v,
            "spike":                (spike_flag, spike_dir),
            "oscillation":          oscillating,
            "persistent_rise":      persistent_rise,
            "persistent_fall":      persistent_fall,
            "consecutive_abnormal": consec_abnormal,
            "time_abnormal_pct":    time_abnormal,
            "deterioration_score":  det_score,
            "confidence":           confidence,
        }
        classification, alert_level, interpretation, causes = classify_parameter(
            parameter, trend_profile
        )

        # ---------- History for sparkline ----------
        history_points = [
            {"t": r.iso_time, "v": r.value}
            for r in history[-8:]  # last 8 points for the mini sparkline
        ]

        return {
            "parameter":              parameter,
            "label":                  meta["label"],
            "unit":                   meta["unit"],
            "abbrev":                 meta["abbrev"],
            "current":                round(current, 2),
            "previous":               round(previous, 2),
            "average":                round(avg, 2) if avg is not None else None,
            "median":                 round(median_v, 2) if median_v is not None else None,
            "minimum":                round(min_v, 2) if min_v is not None else None,
            "maximum":                round(max_v, 2) if max_v is not None else None,
            "std_dev":                round(std_v, 3),
            "slope":                  round(slope, 4),
            "rate_of_change":         round(rate_chg, 2),
            "pct_change":             round(pct_chg, 2),
            "direction":              direction,
            "classification":         classification,
            "alert_level":            alert_level,
            "interpretation":         interpretation,
            "possible_causes":        causes,
            "confidence":             round(confidence, 3),
            "variability_score":      round(variability, 4),
            "consecutive_abnormal":   consec_abnormal,
            "time_abnormal_pct":      round(time_abnormal, 1),
            "deterioration_score":    round(det_score, 3),
            "normal_range":           {"low": low_n, "high": high_n},
            "spike_detected":         spike_flag,
            "oscillation_detected":   oscillating,
            "persistent_rise":        persistent_rise,
            "persistent_fall":        persistent_fall,
            "sample_count":           len(values),
            "time_window_seconds":    len(values) * 2,  # 2-second tick
            "history":                history_points,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _unknown_result(
        self,
        parameter: str,
        meta: dict,
        history: List[TelemetryReading],
    ) -> dict:
        """Return a safe placeholder when there are not enough samples."""
        current = history[-1].value if history else None
        normal  = NORMAL_RANGES.get(parameter, (0.0, float("inf")))
        return {
            "parameter":              parameter,
            "label":                  meta["label"],
            "unit":                   meta["unit"],
            "abbrev":                 meta["abbrev"],
            "current":                round(current, 2) if current is not None else None,
            "previous":               None,
            "average":                None,
            "median":                 None,
            "minimum":                None,
            "maximum":                None,
            "std_dev":                0.0,
            "slope":                  0.0,
            "rate_of_change":         0.0,
            "pct_change":             0.0,
            "direction":              "STABLE",
            "classification":         "Unknown",
            "alert_level":            "WATCH",
            "interpretation":         "Establishing baseline — collecting telemetry samples.",
            "possible_causes":        [],
            "confidence":             0.0,
            "variability_score":      0.0,
            "consecutive_abnormal":   0,
            "time_abnormal_pct":      0.0,
            "deterioration_score":    0.0,
            "normal_range":           {"low": normal[0], "high": normal[1]},
            "spike_detected":         False,
            "oscillation_detected":   False,
            "persistent_rise":        False,
            "persistent_fall":        False,
            "sample_count":           len(history),
            "time_window_seconds":    len(history) * 2,
            "history":                [{"t": r.iso_time, "v": r.value} for r in history[-8:]],
        }


def _moving_toward_normal(slope: float, value: float, low: float, high: float) -> bool:
    """Helper: is the current slope moving the value back toward the normal range?"""
    if value < low:
        return slope > 0
    if value > high:
        return slope < 0
    return True


# Module-level singleton
trend_analyzer = TrendAnalyzer()
