"""
app/telemetry/clinical_rules.py

Modular Clinical Rules Engine for Telemetry Trend Classification.

Responsibilities:
  1. Map a computed trend profile for a parameter to a clinical classification
     (Stable / Improving / Declining / Critical).
  2. Assign a corresponding alert level (NORMAL / WATCH / WARNING / CRITICAL).
  3. Generate a concise clinical interpretation string.
  4. Enumerate possible clinical causes for the observed trend.

Design principles:
  - Each parameter has its own rule function.
  - All functions accept a plain `trend_profile` dict (pure data, no ORM objects).
  - Adding a new parameter requires only adding a new function and registering it
    in RULE_REGISTRY.  Nothing else in the engine changes.
  - Rule functions are pure: same input → same output, no I/O.

Classifications
---------------
  Stable     → Values within normal range, slope near zero.
  Improving  → Values moving back toward normal range.
  Declining  → Values moving away from normal range or worsening.
  Critical   → Values in life-threatening range or deteriorating rapidly.
  Unknown    → Insufficient data to classify.

Alert Levels
------------
  NORMAL   → No action needed.
  WATCH    → Observe closely, re-evaluate at next cycle.
  WARNING  → Clinical review required soon.
  CRITICAL → Immediate intervention required.
"""

from __future__ import annotations

from typing import Callable, Dict, Tuple

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

# (classification, alert_level, interpretation, causes)
RuleResult = Tuple[str, str, str, list]

# A rule function takes the trend_profile dict and returns RuleResult.
RuleFunction = Callable[[dict], RuleResult]


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _is_in_normal(value: float, low: float, high: float) -> bool:
    return low <= value <= high


def _moving_toward_normal(slope: float, value: float, low: float, high: float) -> bool:
    """Return True if the slope direction pushes the value toward the normal range."""
    if value < low:
        return slope > 0  # rising back into range
    if value > high:
        return slope < 0  # falling back into range
    return True           # already in range


# ---------------------------------------------------------------------------
# Individual Parameter Rule Functions
# ---------------------------------------------------------------------------

def _rule_heart_rate(p: dict) -> RuleResult:
    """
    Heart Rate clinical classification rules.
    Normal range: 60–100 bpm.
    """
    val       = p["current"]
    slope     = p["slope"]
    spike, _  = p["spike"]
    osc       = p["oscillation"]
    consec    = p["consecutive_abnormal"]
    det_score = p["deterioration_score"]
    confidence= p["confidence"]

    # Critical: HR > 150 or < 30 with deteriorating trend
    if val > 150 or val < 30:
        return (
            "Critical",
            "CRITICAL",
            f"Extreme heart rate of {val:.0f} bpm requires immediate assessment.",
            ["Severe tachyarrhythmia", "Bradyarrhythmia", "Cardiac arrest risk"],
        )

    # Spike detected
    if spike and val > 110:
        return (
            "Critical",
            "CRITICAL",
            f"Sudden tachycardic spike to {val:.0f} bpm detected.",
            ["Acute pain", "Haemodynamic instability", "Pulmonary embolism", "Septic shock"],
        )

    # Persistent tachycardia with rising slope → severe deterioration
    if val > 120 and slope > 0.4 and consec >= 4:
        return (
            "Critical",
            "CRITICAL",
            f"Persistent and worsening tachycardia: HR {val:.0f} bpm, rising {slope:.2f} bpm/tick.",
            ["Sepsis progression", "Haemodynamic shock", "Hypovolaemia", "Fever"],
        )

    # Tachycardia with rising slope → warning
    if val > 100 and slope > 0.2:
        causes = []
        if slope > 0.5:
            causes = ["Pain", "Anxiety", "Evolving hypovolaemia", "Early sepsis"]
        else:
            causes = ["Pain", "Physiologic stress response", "Medication effect"]
        return (
            "Declining",
            "WARNING",
            f"Continuously rising heart rate: {val:.0f} bpm, slope +{slope:.2f}.",
            causes,
        )

    # Tachycardia, stable
    if val > 100:
        return (
            "Declining",
            "WATCH",
            f"Elevated heart rate at {val:.0f} bpm.  Monitoring for further increase.",
            ["Pain", "Fever", "Dehydration", "Sepsis"],
        )

    # Bradycardia warning
    if val < 50 and slope < -0.2:
        return (
            "Critical",
            "WARNING",
            f"Progressive bradycardia: HR {val:.0f} bpm, falling {slope:.2f} bpm/tick.",
            ["Beta-blocker effect", "Vasovagal response", "Heart block"],
        )

    # Oscillating — physiological instability
    if osc and (val < 60 or val > 100):
        return (
            "Declining",
            "WATCH",
            f"Oscillating heart rate ({val:.0f} bpm) suggests autonomic instability.",
            ["Arrhythmia", "Volume depletion", "Autonomic dysfunction"],
        )

    # Improving: previously elevated, now trending down toward normal
    if 60 <= val <= 100 and slope < -0.1 and p["previous"] > 100:
        return (
            "Improving",
            "NORMAL",
            f"Heart rate normalising from {p['previous']:.0f} to {val:.0f} bpm.",
            [],
        )

    # Stable normal
    if 60 <= val <= 100:
        return (
            "Stable",
            "NORMAL",
            f"Heart rate stable at {val:.0f} bpm within normal range.",
            [],
        )

    return (
        "Unknown",
        "WATCH",
        f"Heart rate {val:.0f} bpm — insufficient data for confident classification.",
        [],
    )


def _rule_map(p: dict) -> RuleResult:
    """
    Mean Arterial Pressure clinical classification rules.
    Normal range: 70–100 mmHg.  Critical threshold: < 65 mmHg.
    """
    val   = p["current"]
    slope = p["slope"]
    consec = p["consecutive_abnormal"]
    prev  = p["previous"]

    # Life-threatening hypotension
    if val < 55:
        return (
            "Critical",
            "CRITICAL",
            f"Critically low MAP {val:.1f} mmHg — severe organ hypoperfusion risk.",
            ["Distributive shock", "Cardiogenic shock", "Haemorrhagic shock", "Vasodilatory crisis"],
        )

    # MAP < 65 (sepsis resuscitation target not met)
    if val < 65 and slope < -0.2:
        return (
            "Critical",
            "CRITICAL",
            f"MAP {val:.1f} mmHg below perfusion threshold, declining {slope:.2f} mmHg/tick.",
            ["Septic shock", "Inadequate vasopressor support", "Fluid deficit"],
        )

    if val < 65:
        return (
            "Declining",
            "WARNING",
            f"MAP {val:.1f} mmHg below 65 mmHg resuscitation target.",
            ["Sepsis", "Vasodilation", "Volume depletion"],
        )

    # Gradual decline from normal — early warning
    if 65 <= val < 70 and slope < -0.3 and consec >= 3:
        return (
            "Declining",
            "WARNING",
            f"Gradual MAP decline from {prev:.1f} to {val:.1f} mmHg — poor perfusion risk.",
            ["Early shock", "Evolving vasodilation", "Inadequate cardiac output"],
        )

    # Hypertensive urgency
    if val > 120:
        return (
            "Declining",
            "WARNING",
            f"MAP critically elevated at {val:.1f} mmHg.",
            ["Hypertensive emergency", "Pain", "Vasopressor excess"],
        )

    # Improving: recovering from low MAP
    if 70 <= val <= 100 and slope > 0.2 and prev < 70:
        return (
            "Improving",
            "NORMAL",
            f"MAP recovering from {prev:.1f} to {val:.1f} mmHg — resuscitation response.",
            [],
        )

    # Stable normal
    if 70 <= val <= 100:
        return (
            "Stable",
            "NORMAL",
            f"MAP {val:.1f} mmHg within normal perfusion range.",
            [],
        )

    return (
        "Unknown",
        "WATCH",
        f"MAP {val:.1f} mmHg — insufficient trend data for classification.",
        [],
    )


def _rule_spo2(p: dict) -> RuleResult:
    """
    SpO2 clinical classification rules.
    Normal range: 95–100 %.
    """
    val   = p["current"]
    slope = p["slope"]
    spike, spike_dir = p["spike"]
    consec = p["consecutive_abnormal"]
    prev  = p["previous"]

    # Critical hypoxia
    if val < 85:
        return (
            "Critical",
            "CRITICAL",
            f"Critical hypoxia: SpO\u2082 {val:.0f}% — immediate oxygen therapy required.",
            ["ARDS", "PE", "Pneumothorax", "Airway obstruction", "Respiratory failure"],
        )

    # Severe hypoxia with declining trend
    if val < 90 and slope < -0.1:
        return (
            "Critical",
            "CRITICAL",
            f"Progressive hypoxia: SpO\u2082 {val:.0f}%, declining {slope:.2f}%/tick.",
            ["Worsening respiratory failure", "ARDS progression", "Pulmonary oedema"],
        )

    # Moderate hypoxia
    if val < 90:
        return (
            "Declining",
            "WARNING",
            f"Low oxygen saturation: SpO\u2082 {val:.0f}% — requires oxygen assessment.",
            ["Atelectasis", "Hypoventilation", "Fluid overload", "Mucus plugging"],
        )

    # Mild hypoxia with declining trend
    if 90 <= val < 95 and slope < -0.15 and consec >= 3:
        return (
            "Declining",
            "WARNING",
            f"Progressive SpO\u2082 decline: {val:.0f}%, slope {slope:.2f}%/tick.",
            ["Respiratory deterioration", "Secretion buildup", "Worsening ventilation-perfusion mismatch"],
        )

    # Borderline
    if 90 <= val < 95:
        return (
            "Declining",
            "WATCH",
            f"SpO\u2082 {val:.0f}% below normal — monitor for further decline.",
            ["Pulmonary pathology", "Medication effect", "Sleep apnoea"],
        )

    # Improving: recovering from hypoxia
    if val >= 95 and slope > 0.1 and prev < 95:
        return (
            "Improving",
            "NORMAL",
            f"SpO\u2082 recovering from {prev:.0f}% to {val:.0f}%.",
            [],
        )

    # Stable normal
    if val >= 95:
        return (
            "Stable",
            "NORMAL",
            f"SpO\u2082 {val:.0f}% within normal saturation range.",
            [],
        )

    return (
        "Unknown",
        "WATCH",
        f"SpO\u2082 {val:.0f}% — insufficient data for classification.",
        [],
    )


def _rule_respiratory_rate(p: dict) -> RuleResult:
    """
    Respiratory Rate clinical classification rules.
    Normal range: 12–20 breaths/min.
    """
    val   = p["current"]
    slope = p["slope"]
    consec = p["consecutive_abnormal"]

    # Severe tachypnoea
    if val > 30 and slope > 0.2:
        return (
            "Critical",
            "CRITICAL",
            f"Severe and worsening tachypnoea: RR {val:.0f} bpm, slope +{slope:.2f}.",
            ["Respiratory failure", "Metabolic acidosis compensation", "Sepsis", "PE"],
        )

    if val > 30:
        return (
            "Declining",
            "WARNING",
            f"Marked tachypnoea: RR {val:.0f} breaths/min.",
            ["Respiratory distress", "Pain", "Fever", "ARDS", "Metabolic acidosis"],
        )

    # Moderate tachypnoea with rising trend
    if val > 24 and slope > 0.15:
        return (
            "Declining",
            "WARNING",
            f"Rising respiratory rate: {val:.0f} breaths/min, trend worsening.",
            ["Worsening pulmonary condition", "Fever", "Early shock"],
        )

    if val > 20 and slope > 0.1 and consec >= 3:
        return (
            "Declining",
            "WATCH",
            f"Mild tachypnoea with persistent rise: RR {val:.0f} bpm.",
            ["Anxiety", "Pain", "Infection", "Airway irritation"],
        )

    # Bradypnoea
    if val < 10:
        return (
            "Critical",
            "CRITICAL",
            f"Bradypnoea: RR {val:.0f} breaths/min — respiratory depression risk.",
            ["Opioid sedation", "Central nervous system depression", "Neuromuscular disease"],
        )

    # Improving
    if 12 <= val <= 20 and slope < -0.1 and p["previous"] > 20:
        return (
            "Improving",
            "NORMAL",
            f"Respiratory rate normalising: {p['previous']:.0f} → {val:.0f} breaths/min.",
            [],
        )

    # Stable normal
    if 12 <= val <= 20:
        return (
            "Stable",
            "NORMAL",
            f"Respiratory rate {val:.0f} breaths/min within normal range.",
            [],
        )

    return (
        "Unknown",
        "WATCH",
        f"Respiratory rate {val:.0f} — data insufficient for confident trend.",
        [],
    )


def _rule_temperature(p: dict) -> RuleResult:
    """
    Temperature clinical classification rules.
    Normal range: 36.1–37.9°C.
    """
    val   = p["current"]
    slope = p["slope"]
    prev  = p["previous"]

    # Hyperpyrexia
    if val > 40.0:
        return (
            "Critical",
            "CRITICAL",
            f"Hyperpyrexia: {val:.1f}\u00b0C — risk of systemic decompensation.",
            ["Severe infection / sepsis", "Heat stroke", "Central fever", "Malignant hyperthermia"],
        )

    # High fever with rising trend
    if val > 39.0 and slope > 0.01:
        return (
            "Declining",
            "WARNING",
            f"Rising fever: {val:.1f}\u00b0C, slope +{slope:.3f}\u00b0C/tick.",
            ["Active infection", "Sepsis", "Inflammatory response", "Drug fever"],
        )

    # Moderate fever
    if val > 38.5:
        return (
            "Declining",
            "WATCH",
            f"Elevated temperature {val:.1f}\u00b0C — possible infection marker.",
            ["Infection", "Post-operative inflammation", "Atelectasis"],
        )

    # Hypothermia
    if val < 35.5 and slope < -0.01:
        return (
            "Critical",
            "CRITICAL",
            f"Progressive hypothermia: {val:.1f}\u00b0C — risk of coagulopathy.",
            ["Septic shock", "Environmental exposure", "Hypothyroidism"],
        )

    if val < 36.0:
        return (
            "Declining",
            "WATCH",
            f"Sub-normal temperature {val:.1f}\u00b0C — monitor for hypothermia.",
            ["Vasodilation", "Volume depletion", "Septic shock (late)"],
        )

    # Improving: defervescence
    if 36.1 <= val <= 37.9 and slope < -0.01 and prev > 38.5:
        return (
            "Improving",
            "NORMAL",
            f"Temperature defervescing from {prev:.1f}\u00b0C to {val:.1f}\u00b0C.",
            [],
        )

    # Stable normal
    if 36.1 <= val <= 37.9:
        return (
            "Stable",
            "NORMAL",
            f"Temperature {val:.1f}\u00b0C within normal range.",
            [],
        )

    return (
        "Unknown",
        "WATCH",
        f"Temperature {val:.1f}\u00b0C — inconclusive trend data.",
        [],
    )


def _rule_systolic_bp(p: dict) -> RuleResult:
    """
    Systolic BP clinical classification rules.
    Normal range: 90–140 mmHg.
    """
    val   = p["current"]
    slope = p["slope"]
    consec = p["consecutive_abnormal"]
    prev  = p["previous"]

    # Hypotensive crisis
    if val < 70:
        return (
            "Critical",
            "CRITICAL",
            f"Severe hypotension: SBP {val:.0f} mmHg — haemodynamic collapse risk.",
            ["Septic shock", "Cardiogenic shock", "Haemorrhage", "Vasodilatory crisis"],
        )

    # Hypotension with declining slope
    if val < 90 and slope < -0.3 and consec >= 3:
        return (
            "Critical",
            "CRITICAL",
            f"Persistent hypotension with worsening trend: SBP {val:.0f} mmHg.",
            ["Shock progression", "Vasopressor failure", "Volume depletion"],
        )

    if val < 90:
        return (
            "Declining",
            "WARNING",
            f"Hypotension: SBP {val:.0f} mmHg — review fluid status and vasopressors.",
            ["Hypovolaemia", "Sepsis", "Cardiac dysfunction"],
        )

    # Hypertensive urgency
    if val > 180:
        return (
            "Critical",
            "WARNING",
            f"Severe hypertension: SBP {val:.0f} mmHg — urgent antihypertensive review.",
            ["Hypertensive urgency", "Pain", "Increased ICP"],
        )

    # Improving hypotension
    if 90 <= val <= 140 and slope > 0.2 and prev < 90:
        return (
            "Improving",
            "NORMAL",
            f"Systolic BP recovering: {prev:.0f} → {val:.0f} mmHg.",
            [],
        )

    # Stable normal
    if 90 <= val <= 140:
        return (
            "Stable",
            "NORMAL",
            f"Systolic BP {val:.0f} mmHg within normal range.",
            [],
        )

    return (
        "Unknown",
        "WATCH",
        f"Systolic BP {val:.0f} mmHg — trend data insufficient.",
        [],
    )


def _rule_diastolic_bp(p: dict) -> RuleResult:
    """
    Diastolic BP clinical classification rules.
    Normal range: 60–90 mmHg.
    """
    val   = p["current"]
    slope = p["slope"]
    prev  = p["previous"]

    if val < 40 and slope < -0.2:
        return (
            "Critical",
            "CRITICAL",
            f"Critically low diastolic pressure: DBP {val:.0f} mmHg — cardiac filling risk.",
            ["Distributive shock", "Aortic regurgitation", "Vasodilatory shock"],
        )

    if val < 50:
        return (
            "Declining",
            "WARNING",
            f"Low diastolic pressure: DBP {val:.0f} mmHg — assess cardiac perfusion.",
            ["Vasodilation", "Volume depletion"],
        )

    if val > 110:
        return (
            "Declining",
            "WARNING",
            f"Elevated diastolic pressure: DBP {val:.0f} mmHg.",
            ["Hypertensive emergency", "Pain", "Renal disease"],
        )

    # Improving
    if 60 <= val <= 90 and slope > 0.1 and prev < 60:
        return (
            "Improving",
            "NORMAL",
            f"Diastolic BP recovering: {prev:.0f} → {val:.0f} mmHg.",
            [],
        )

    # Stable normal
    if 60 <= val <= 90:
        return (
            "Stable",
            "NORMAL",
            f"Diastolic BP {val:.0f} mmHg within normal range.",
            [],
        )

    return (
        "Unknown",
        "WATCH",
        f"Diastolic BP {val:.0f} mmHg — insufficient trend data.",
        [],
    )


# ---------------------------------------------------------------------------
# Rule Registry
# ---------------------------------------------------------------------------
# Maps parameter key → rule function.
# To add a new parameter (e.g. "shock_index"), create a rule function and add
# it here.  No other module needs to change.

RULE_REGISTRY: Dict[str, RuleFunction] = {
    "heart_rate":       _rule_heart_rate,
    "map":              _rule_map,
    "spo2":             _rule_spo2,
    "respiratory_rate": _rule_respiratory_rate,
    "temperature":      _rule_temperature,
    "systolic_bp":      _rule_systolic_bp,
    "diastolic_bp":     _rule_diastolic_bp,
}

# Severity ordering for worst-case rollup
ALERT_SEVERITY: Dict[str, int] = {
    "NORMAL":   0,
    "WATCH":    1,
    "WARNING":  2,
    "CRITICAL": 3,
}

CLASSIFICATION_SEVERITY: Dict[str, int] = {
    "Stable":    0,
    "Unknown":   0,
    "Improving": 0,
    "Declining": 1,
    "Critical":  2,
}


def classify_parameter(parameter: str, trend_profile: dict) -> RuleResult:
    """
    Apply clinical rules to a parameter's trend profile.

    Parameters
    ----------
    parameter : str
        One of the keys in RULE_REGISTRY.
    trend_profile : dict
        Must contain at minimum:
        - current, previous, slope, spike (bool, dir), oscillation, consecutive_abnormal,
          deterioration_score, confidence.

    Returns
    -------
    (classification, alert_level, interpretation, causes)
    """
    rule_fn = RULE_REGISTRY.get(parameter)
    if rule_fn is None:
        return (
            "Unknown",
            "WATCH",
            f"No clinical rules registered for parameter '{parameter}'.",
            [],
        )
    try:
        return rule_fn(trend_profile)
    except Exception as exc:
        return (
            "Unknown",
            "WATCH",
            f"Rule evaluation error for '{parameter}': {exc}",
            [],
        )
