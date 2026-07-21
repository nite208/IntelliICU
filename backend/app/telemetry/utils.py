"""
app/telemetry/utils.py

Pure Mathematical Utilities for Telemetry Trend Analysis.

All functions are stateless, have no side effects, and accept plain Python lists.
They operate in O(n) time where n is the number of samples.

These utilities can be extended with additional statistical functions without
affecting any other module.  They are deliberately free of any clinical knowledge
so they remain reusable across future trend types (ventilator, lab, SOFA, etc.).
"""

from __future__ import annotations

import math
import statistics
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Basic Statistics
# ---------------------------------------------------------------------------

def compute_mean(values: List[float]) -> Optional[float]:
    """Arithmetic mean.  Returns None for empty input."""
    if not values:
        return None
    return statistics.mean(values)


def compute_median(values: List[float]) -> Optional[float]:
    """Median value.  Returns None for empty input."""
    if not values:
        return None
    return statistics.median(values)


def compute_std(values: List[float]) -> float:
    """
    Population standard deviation.
    Returns 0.0 for a single sample (variance undefined).
    """
    if len(values) < 2:
        return 0.0
    return statistics.pstdev(values)


def compute_min(values: List[float]) -> Optional[float]:
    return min(values) if values else None


def compute_max(values: List[float]) -> Optional[float]:
    return max(values) if values else None


# ---------------------------------------------------------------------------
# Rate & Slope
# ---------------------------------------------------------------------------

def compute_slope(values: List[float]) -> float:
    """
    Linear regression slope via least-squares over equally spaced samples.

    Uses index positions (0, 1, 2, ..., n-1) as the x-axis, which corresponds
    to equal time intervals (simulator tick = 2 s).

    Returns 0.0 for fewer than 2 samples.
    Units: value-units per sample (e.g. bpm per 2-second tick).
    """
    n = len(values)
    if n < 2:
        return 0.0

    x_mean = (n - 1) / 2.0
    y_mean = statistics.mean(values)

    numerator = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))

    if denominator == 0:
        return 0.0
    return numerator / denominator


def compute_rate_of_change(current: float, previous: float) -> float:
    """
    Absolute change from previous to current.
    Positive → rising, negative → falling.
    """
    return current - previous


def compute_pct_change(current: float, reference: float) -> float:
    """
    Percentage change relative to reference value.
    Returns 0.0 when reference is zero to avoid division errors.
    """
    if reference == 0.0:
        return 0.0
    return ((current - reference) / abs(reference)) * 100.0


# ---------------------------------------------------------------------------
# Trend Confidence
# ---------------------------------------------------------------------------

def compute_trend_confidence(values: List[float], slope: float) -> float:
    """
    Estimate confidence [0.0, 1.0] that the computed slope reflects a real trend.

    Method: coefficient of determination (R²) of the linear fit.
    High R² → the data follows a consistent linear trajectory → high confidence.
    Low R²  → noisy / oscillating signal → low confidence.
    """
    n = len(values)
    if n < 3:
        return 0.0

    x_mean = (n - 1) / 2.0
    y_mean = statistics.mean(values)

    ss_res = sum(
        (v - (y_mean + slope * (i - x_mean))) ** 2
        for i, v in enumerate(values)
    )
    ss_tot = sum((v - y_mean) ** 2 for v in values)

    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0

    r_squared = max(0.0, 1.0 - ss_res / ss_tot)
    return round(r_squared, 3)


# ---------------------------------------------------------------------------
# Pattern Detection
# ---------------------------------------------------------------------------

def detect_spike(values: List[float], threshold_std: float = 2.5) -> Tuple[bool, str]:
    """
    Detect a sudden spike or drop using z-score of the latest sample.

    Returns (detected: bool, direction: 'UP' | 'DOWN' | 'NONE').
    threshold_std: number of standard deviations above/below the rolling mean.
    """
    if len(values) < 4:
        return False, "NONE"
    baseline = values[:-1]
    mean_b = statistics.mean(baseline)
    std_b = statistics.pstdev(baseline)
    if std_b == 0:
        return False, "NONE"
    z = (values[-1] - mean_b) / std_b
    if z > threshold_std:
        return True, "UP"
    if z < -threshold_std:
        return True, "DOWN"
    return False, "NONE"


def detect_oscillation(values: List[float], min_reversals: int = 3) -> bool:
    """
    Detect oscillating (alternating up/down) behaviour.

    Counts direction reversals in the value sequence.  More than `min_reversals`
    reversals in n samples indicates an oscillating pattern.
    """
    if len(values) < 4:
        return False
    reversals = 0
    for i in range(1, len(values) - 1):
        prev_dir = values[i] - values[i - 1]
        next_dir = values[i + 1] - values[i]
        if prev_dir * next_dir < 0:
            reversals += 1
    return reversals >= min_reversals


def detect_persistent_trend(
    values: List[float],
    direction: str,
    min_consecutive: int = 4,
) -> bool:
    """
    Detect a persistent (non-oscillating) monotonic trend.

    Parameters
    ----------
    direction : 'UP' | 'DOWN'
    min_consecutive : minimum number of consecutive samples moving in `direction`.
    """
    if len(values) < min_consecutive + 1:
        return False
    target_values = values[-(min_consecutive + 1):]
    if direction == "UP":
        return all(target_values[i] < target_values[i + 1] for i in range(min_consecutive))
    if direction == "DOWN":
        return all(target_values[i] > target_values[i + 1] for i in range(min_consecutive))
    return False


# ---------------------------------------------------------------------------
# Variability
# ---------------------------------------------------------------------------

def compute_variability_score(values: List[float]) -> float:
    """
    Normalized variability score [0.0, 1.0].

    Based on the coefficient of variation (CV = std / mean).
    Capped at 1.0.  A score near 0 indicates a very stable signal.
    """
    if len(values) < 2:
        return 0.0
    mean_v = statistics.mean(values)
    if mean_v == 0:
        return 0.0
    cv = statistics.pstdev(values) / abs(mean_v)
    return round(min(cv, 1.0), 4)


# ---------------------------------------------------------------------------
# Abnormality Counters
# ---------------------------------------------------------------------------

def count_consecutive_abnormal(
    values: List[float],
    low: float,
    high: float,
) -> int:
    """
    Count consecutive samples from the end that fall outside [low, high].
    """
    count = 0
    for v in reversed(values):
        if v < low or v > high:
            count += 1
        else:
            break
    return count


def compute_time_abnormal_pct(
    values: List[float],
    low: float,
    high: float,
) -> float:
    """
    Percentage of samples that are outside the normal range [low, high].
    """
    if not values:
        return 0.0
    abnormal = sum(1 for v in values if v < low or v > high)
    return round((abnormal / len(values)) * 100.0, 1)


# ---------------------------------------------------------------------------
# Early Deterioration Score
# ---------------------------------------------------------------------------

def compute_early_deterioration_score(
    slope: float,
    pct_change: float,
    consecutive_abnormal: int,
    time_abnormal_pct: float,
    is_deteriorating_direction: bool,
) -> float:
    """
    Composite early deterioration score [0.0, 1.0].

    Combines:
    - Slope magnitude (normalised to 0.1 per unit/tick)
    - Percentage change magnitude (normalised to 20%)
    - Consecutive abnormal samples count (normalised to window of 10)
    - Time spent abnormal percentage
    - Direction penalty if moving away from normal

    Higher score → more evidence of early deterioration.
    """
    if not is_deteriorating_direction:
        return 0.0

    slope_score = min(abs(slope) / 0.1, 1.0) * 0.30
    pct_score = min(abs(pct_change) / 20.0, 1.0) * 0.25
    consec_score = min(consecutive_abnormal / 10.0, 1.0) * 0.25
    time_score = min(time_abnormal_pct / 100.0, 1.0) * 0.20

    total = slope_score + pct_score + consec_score + time_score
    return round(min(total, 1.0), 3)
