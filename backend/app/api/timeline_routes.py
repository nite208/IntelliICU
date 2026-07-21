from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
import io

from app.services.timeline_engine import timeline_engine
from app.websocket.simulator import simulator

router = APIRouter(
    prefix="/timeline",
    tags=["Clinical Timeline"],
)

@router.get("/{patient_id}")
async def get_timeline(
    patient_id: str,
    event_type: str = Query(None, alias="type"),
    search: str = Query(None)
):
    """
    Get timeline events for a patient with optional type filter and search query.
    """
    # Verify patient exists
    if patient_id != "SYSTEM":
        patient = next((p for p in simulator.patients if p["id"] == patient_id), None)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

    events = timeline_engine.get_patient_timeline(patient_id, event_type, search)
    return events

@router.post("/{patient_id}")
async def log_event(
    patient_id: str,
    payload: dict
):
    """
    Log a new timeline event for a patient.
    """
    if patient_id != "SYSTEM":
        patient = next((p for p in simulator.patients if p["id"] == patient_id), None)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

    event = timeline_engine.add_event(
        patient_id=patient_id,
        event_type=payload.get("type", "User"),
        title=payload.get("title", "Clinical Action"),
        description=payload.get("description", ""),
        actor=payload.get("actor", "System"),
        metadata=payload.get("metadata", {})
    )
    return event

@router.get("/{patient_id}/export")
async def export_timeline(
    patient_id: str,
    format: str = Query("json"),
    event_type: str = Query(None, alias="type"),
    search: str = Query(None)
):
    """
    Export patient timeline in CSV, JSON, or PDF format.
    """
    patient_name = "System Logs"
    if patient_id != "SYSTEM":
        patient = next((p for p in simulator.patients if p["id"] == patient_id), None)
        patient_name = patient["name"] if patient else "Unknown"


    events = timeline_engine.get_patient_timeline(patient_id, event_type, search)

    if format == "csv":
        data = timeline_engine.export_csv(patient_id, events)
        return StreamingResponse(
            io.StringIO(data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=timeline_{patient_id}.csv"}
        )
    elif format == "pdf":
        data = timeline_engine.export_pdf(patient_id, events, patient_name)
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=timeline_{patient_id}.pdf"}
        )
    else:
        # Default: JSON
        data = timeline_engine.export_json(patient_id, events)
        return Response(
            content=data,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=timeline_{patient_id}.json"}
        )
