"""
app/telemetry/store.py

Enterprise Telemetry Rolling-Window Store.

Maintains a thread-safe, per-patient, per-parameter rolling buffer of the last N
telemetry readings.  The store is the single source of truth for all raw samples —
no database, no I/O.  It is designed for O(1) ingest and O(n) query where n is
the window size (default 30 samples ≈ 60 seconds at the 2-second simulator tick).

Extending the store to track additional parameters (SOFA score, NEWS2, Shock Index,
etc.) requires only adding the parameter key to TRACKED_PARAMETERS and calling
`ingest()` with a dict that includes that key.  No other files need to change.
"""

from __future__ import annotations

import threading
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Maximum number of readings retained per patient per parameter.
# At the 2-second simulator tick this represents ~60 seconds of history.
WINDOW_SIZE: int = 30

# The canonical set of telemetry parameters this engine tracks.
# Each key maps exactly to the field name present in the simulator patient dict
# OR is derived in-store (e.g. MAP is computed from systolic/diastolic).
TRACKED_PARAMETERS: tuple[str, ...] = (
    "heart_rate",
    "systolic_bp",
    "diastolic_bp",
    "map",           # computed — not from the dict directly
    "respiratory_rate",
    "spo2",
    "temperature",
)

# Human-readable labels and clinical units for each parameter.
PARAMETER_META: Dict[str, Dict[str, str]] = {
    "heart_rate":       {"label": "Heart Rate",       "unit": "bpm",   "abbrev": "HR"},
    "systolic_bp":      {"label": "Systolic BP",       "unit": "mmHg",  "abbrev": "SBP"},
    "diastolic_bp":     {"label": "Diastolic BP",      "unit": "mmHg",  "abbrev": "DBP"},
    "map":              {"label": "MAP",                "unit": "mmHg",  "abbrev": "MAP"},
    "respiratory_rate": {"label": "Respiratory Rate",  "unit": "bpm",   "abbrev": "RR"},
    "spo2":             {"label": "SpO\u2082",           "unit": "%",     "abbrev": "SpO\u2082"},
    "temperature":      {"label": "Temperature",        "unit": "\u00b0C", "abbrev": "Temp"},
}

# Normal physiological ranges used in alert rule evaluation.
# Format: (low_normal, high_normal)
NORMAL_RANGES: Dict[str, tuple[float, float]] = {
    "heart_rate":        (60.0,  100.0),
    "systolic_bp":       (90.0,  140.0),
    "diastolic_bp":      (60.0,   90.0),
    "map":               (70.0,  100.0),
    "respiratory_rate":  (12.0,   20.0),
    "spo2":              (95.0,  100.0),
    "temperature":       (36.1,   37.9),
}


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

class TelemetryReading:
    """
    A single timestamped telemetry sample for one parameter.

    Kept as a plain class (not a Pydantic model) for minimal allocation overhead
    during the high-frequency ingest path.
    """

    __slots__ = ("timestamp", "value", "iso_time")

    def __init__(self, value: float, timestamp: Optional[datetime] = None) -> None:
        self.value: float = value
        self.timestamp: datetime = timestamp or datetime.utcnow()
        self.iso_time: str = self.timestamp.strftime("%H:%M:%S")

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "timestamp": self.iso_time,
        }


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------

class TelemetryStore:
    """
    Thread-safe, in-memory rolling window store for ICU telemetry.

    Structure (logical):

        store
        └── patient_id (str)
            └── parameter (str)
                └── deque[TelemetryReading]  (maxlen = WINDOW_SIZE)

    The store is a singleton.  Access via the module-level `telemetry_store`
    instance exposed by this module.
    """

    def __init__(self, window_size: int = WINDOW_SIZE) -> None:
        self._window_size: int = window_size
        # patient_id -> parameter -> deque[TelemetryReading]
        self._data: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: {param: deque(maxlen=self._window_size) for param in TRACKED_PARAMETERS}
        )
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------

    def ingest(self, patient_id: str, vitals: dict) -> None:
        """
        Push the latest vital sign dict into the rolling window.

        Computes MAP in-store so callers don't need to know the formula.

        Parameters
        ----------
        patient_id : str
            Unique patient identifier matching the simulator patient dict.
        vitals : dict
            Keys must include at minimum: heart_rate, systolic_bp, diastolic_bp,
            respiratory_rate, spo2, temperature.  Extra keys are silently ignored.
        """
        now = datetime.utcnow()

        sbp = float(vitals.get("systolic_bp", 0))
        dbp = float(vitals.get("diastolic_bp", 0))
        map_value = round(dbp + (sbp - dbp) / 3.0, 1) if sbp and dbp else 0.0

        with self._lock:
            bucket = self._data[patient_id]
            for param in TRACKED_PARAMETERS:
                if param == "map":
                    raw_value = map_value
                else:
                    raw_value = vitals.get(param)
                    if raw_value is None:
                        continue
                    raw_value = float(raw_value)
                bucket[param].append(TelemetryReading(value=raw_value, timestamp=now))

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def get_history(self, patient_id: str, parameter: str) -> List[TelemetryReading]:
        """
        Return the ordered (oldest → newest) history for a given parameter.

        Returns an empty list if the patient or parameter is not known.
        """
        with self._lock:
            if patient_id not in self._data:
                return []
            return list(self._data[patient_id].get(parameter, []))

    def get_all_patients(self) -> List[str]:
        """Return the list of patient IDs currently held in the store."""
        with self._lock:
            return list(self._data.keys())

    def get_patient_snapshot(self, patient_id: str) -> Dict[str, List[TelemetryReading]]:
        """
        Return a shallow copy of all parameter histories for a patient.

        Used by the TrendAnalyzer to avoid holding the lock during computation.
        """
        with self._lock:
            if patient_id not in self._data:
                return {}
            return {param: list(deq) for param, deq in self._data[patient_id].items()}

    def get_latest_value(self, patient_id: str, parameter: str) -> Optional[float]:
        """Return the most recent value for a parameter, or None if unavailable."""
        history = self.get_history(patient_id, parameter)
        return history[-1].value if history else None

    def patient_has_data(self, patient_id: str, min_samples: int = 2) -> bool:
        """Return True if the patient has at least `min_samples` in any parameter."""
        with self._lock:
            if patient_id not in self._data:
                return False
            return any(len(deq) >= min_samples for deq in self._data[patient_id].values())


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

telemetry_store = TelemetryStore()
