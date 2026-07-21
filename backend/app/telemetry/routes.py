"""
app/telemetry/routes.py

Telemetry REST API Routes.

Endpoints:
  GET /api/telemetry/trends             → all patients summary dict
  GET /api/telemetry/trends/{id}        → single patient full summary
  GET /api/telemetry/history/{id}/{param} → raw reading history list
  GET /api/telemetry/summary/{id}       → compact narrative + alert level

All responses draw from the TelemetryEngine cache populated by the simulator loop.
No database access.  No heavy computation on the request path.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.telemetry.trend_engine import telemetry_engine
from app.telemetry.store import TRACKED_PARAMETERS, PARAMETER_META

router = APIRouter(
    prefix="/telemetry",
    tags=["Telemetry"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/trends", summary="All Patients Trend Summary")
def get_all_trends():
    """
    Return the latest trend summary for every patient currently tracked.
    Draws from the in-memory cache — responds instantly.
    """
    return {
        "patients": telemetry_engine.get_all_cached_summaries(),
        "patient_count": len(telemetry_engine.get_all_patient_ids()),
        "tracked_parameters": list(TRACKED_PARAMETERS),
    }


@router.get("/trends/{patient_id}", summary="Single Patient Trend Summary")
def get_patient_trends(patient_id: str):
    """
    Return the full trend summary for a specific patient.
    Triggers a fresh analysis run to return the most recent result.
    """
    if patient_id not in telemetry_engine.get_all_patient_ids():
        raise HTTPException(
            status_code=404,
            detail=f"Patient '{patient_id}' not found in telemetry store. "
                   "Ensure the simulator has ingested at least one reading.",
        )
    return telemetry_engine.analyze_patient(patient_id)


@router.get("/history/{patient_id}/{parameter}", summary="Raw Parameter History")
def get_parameter_history(patient_id: str, parameter: str):
    """
    Return the raw rolling-window history for a specific parameter.

    Useful for debugging or offline plotting.
    """
    if parameter not in TRACKED_PARAMETERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown parameter '{parameter}'. "
                   f"Valid options: {list(TRACKED_PARAMETERS)}",
        )
    history = telemetry_engine.get_history_for_api(patient_id, parameter)
    meta = PARAMETER_META.get(parameter, {})
    return {
        "patient_id": patient_id,
        "parameter":  parameter,
        "label":      meta.get("label", parameter),
        "unit":       meta.get("unit", ""),
        "count":      len(history),
        "history":    history,
    }


@router.get("/summary/{patient_id}", summary="Patient Trend Narrative Summary")
def get_patient_summary(patient_id: str):
    """
    Return a compact summary containing:
    - overall_classification
    - overall_alert_level
    - clinical_narrative
    - combined_deterioration_score
    - timeline events

    Intended for the sidebar summary card that does not need full per-parameter data.
    """
    cached = telemetry_engine.get_cached_summary(patient_id)
    if not cached:
        # If not cached yet, attempt a fresh analysis
        all_ids = telemetry_engine.get_all_patient_ids()
        if patient_id not in all_ids:
            return {
                "patient_id":                patient_id,
                "overall_classification":    "Unknown",
                "overall_alert_level":       "WATCH",
                "clinical_narrative":        "Collecting telemetry — analysis pending.",
                "combined_deterioration_score": 0.0,
                "timeline":                  [],
            }
        cached = telemetry_engine.analyze_patient(patient_id)

    return {
        "patient_id":                cached.get("patient_id"),
        "patient_name":              cached.get("patient_name", ""),
        "timestamp":                 cached.get("timestamp"),
        "overall_classification":    cached.get("overall_classification"),
        "overall_alert_level":       cached.get("overall_alert_level"),
        "alert_color":               cached.get("alert_color"),
        "clinical_narrative":        cached.get("clinical_narrative"),
        "combined_deterioration_score": cached.get("combined_deterioration_score"),
        "timeline":                  cached.get("timeline", []),
    }
