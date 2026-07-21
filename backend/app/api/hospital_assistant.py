"""
app/api/hospital_assistant.py

Hospital Assistant REST API.

Endpoints:
  GET  /api/hospital-assistant/snapshot  → full hospital snapshot (no LLM)
  POST /api/hospital-assistant/chat      → natural language hospital query (batch or SSE)
  GET  /api/hospital-assistant/summary   → compact headline KPIs
  GET  /api/hospital-assistant/alerts    → all active abnormal-parameter alerts
  GET  /api/hospital-assistant/critical  → ranked critical patient list
  GET  /api/hospital-assistant/insights  → AI insights + recommended actions
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.hospital_assistant_service import hospital_assistant

router = APIRouter(
    prefix="/hospital-assistant",
    tags=["Hospital Assistant"],
)


# ---------------------------------------------------------------------------
# Request/Response schemas
# ---------------------------------------------------------------------------

class HospitalChatRequest(BaseModel):
    question:   str = Field(..., description="Hospital-level clinical question")
    session_id: str = Field(default="hospital", description="Chat session identifier")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/snapshot", summary="Full Hospital Snapshot")
def get_snapshot():
    """
    Return the complete real-time hospital snapshot:
    patients ranked, critical list, active alerts, telemetry insights, AI insights,
    recommended actions.  No LLM call — purely deterministic aggregation.
    """
    return hospital_assistant.build_hospital_snapshot()


@router.get("/summary", summary="Hospital KPI Summary")
def get_summary():
    """Compact headline KPIs — total patients, critical count, bed occupancy, etc."""
    snapshot = hospital_assistant.build_hospital_snapshot()
    return snapshot["summary"]


@router.get("/alerts", summary="Active Clinical Alerts")
def get_alerts():
    """All patients with at least one abnormal clinical parameter."""
    snapshot = hospital_assistant.build_hospital_snapshot()
    return {
        "alert_count": len(snapshot["active_alerts"]),
        "alerts":      snapshot["active_alerts"],
    }


@router.get("/critical", summary="Critical Patient Ranking")
def get_critical():
    """Ranked list of critical / high-risk patients."""
    snapshot = hospital_assistant.build_hospital_snapshot()
    return {
        "critical_count": len(snapshot["critical_patients"]),
        "patients":       snapshot["critical_patients"],
    }


@router.get("/insights", summary="AI Insights and Recommended Actions")
def get_insights():
    """AI-generated hospital-level insights and prioritised action list."""
    snapshot = hospital_assistant.build_hospital_snapshot()
    return {
        "ai_insights":         snapshot["ai_insights"],
        "recommended_actions": snapshot["recommended_actions"],
        "telemetry_insights":  snapshot["telemetry_insights"],
    }


@router.post("/chat", summary="Hospital AI Assistant Chat")
def chat(request: HospitalChatRequest, stream: bool = False):
    """
    Answer a hospital-level clinical question.

    Supports:
    - Batch mode (default): returns a full structured JSON response.
    - Streaming mode (?stream=true): returns SSE text/event-stream.

    Example questions:
    - "Which patients need immediate attention?"
    - "Show highest risk ICU patients"
    - "Give me a sepsis overview"
    - "Which patients have worsening vital trends?"
    """
    if stream:
        gen = hospital_assistant.ask_stream(
            question=request.question,
            session_id=request.session_id,
        )
        return StreamingResponse(gen, media_type="text/event-stream")
    return hospital_assistant.ask(
        question=request.question,
        session_id=request.session_id,
    )
