"""
Patient WebSocket Routes

Provides real-time streaming for an individual patient.

Endpoint:
    ws://localhost:8000/ws/patient/{patient_id}
"""

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/patient/{patient_id}")
async def patient_websocket(
    websocket: WebSocket,
    patient_id: str,
):
    """
    Individual Patient Live Stream

    Each connected client receives live updates only for the requested patient.
    """

    await manager.connect_patient(patient_id, websocket)

    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                # No message from client in 30s — keep the connection alive.
                continue

    except WebSocketDisconnect:
        manager.disconnect_patient(patient_id, websocket)

    except Exception as exc:
        print(f"[ERROR] Patient WebSocket Error ({patient_id}): {exc}")
        manager.disconnect_patient(patient_id, websocket)