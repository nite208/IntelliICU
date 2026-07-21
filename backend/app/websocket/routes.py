"""
WebSocket Routes
"""

import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    """
    Live Dashboard WebSocket

    Accepts connections and keeps them alive.
    The simulator broadcasts to all connected clients every 2 seconds.
    The client does not need to send any messages.
    """

    await manager.connect(websocket)

    try:
        while True:
            # Use a short receive with timeout so we can detect stale
            # connections promptly without blocking the event loop.
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                # No message from client in 30s — that's fine, keep alive.
                continue

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception:
        # Catch any other transport error (TLS teardown, RST, etc.)
        manager.disconnect(websocket)