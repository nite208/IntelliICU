"""
Enterprise WebSocket Connection Manager

Supports:
- Dashboard Connections
- Patient Connections
- Alert Connections
- ICU Monitor Connections

Author: IntelliICU
"""

from collections import defaultdict
from typing import Dict, List

import json

from fastapi import WebSocket


class ConnectionManager:
    """
    Enterprise WebSocket Connection Manager

    This manager supports multiple independent WebSocket channels.

    Channels:
    ---------
    Dashboard
        Live dashboard metrics.

    Patient
        Individual patient live stream.

    Alerts
        Global alert center.

    Monitor
        ICU monitor streaming.
    """

    def __init__(self):

        # ---------------------------------------
        # Legacy Dashboard Connections
        # ---------------------------------------
        self.dashboard_connections: List[WebSocket] = []

        # ---------------------------------------
        # Patient Connections
        # patient_id -> list[WebSocket]
        # ---------------------------------------
        self.patient_connections: Dict[
            str,
            List[WebSocket]
        ] = defaultdict(list)

        # ---------------------------------------
        # Alert Connections
        # ---------------------------------------
        self.alert_connections: List[WebSocket] = []

        # ---------------------------------------
        # ICU Monitor Connections
        # ---------------------------------------
        self.monitor_connections: List[WebSocket] = []

    # =====================================================
    # Dashboard
    # =====================================================

    async def connect(self, websocket: WebSocket):
        """
        Backward compatible dashboard connect.
        """

        await self.connect_dashboard(websocket)

    async def connect_dashboard(
        self,
        websocket: WebSocket,
    ):
        """
        Connect Dashboard Client
        """

        await websocket.accept()

        self.dashboard_connections.append(websocket)

        print(
            f"[OK] Dashboard Connected | "
            f"{len(self.dashboard_connections)} clients"
        )

    def disconnect(
        self,
        websocket: WebSocket,
    ):
        """
        Backward compatible disconnect.
        """

        self.disconnect_dashboard(websocket)

    def disconnect_dashboard(
        self,
        websocket: WebSocket,
    ):

        if websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)

        print(
            f"[DISCONNECT] Dashboard Disconnected | "
            f"{len(self.dashboard_connections)} clients"
        )

    # =====================================================
    # Patient
    # =====================================================

    async def connect_patient(
        self,
        patient_id: str,
        websocket: WebSocket,
    ):

        await websocket.accept()

        self.patient_connections[
            patient_id
        ].append(websocket)

        print(
            f"[PATIENT CONNECT] Patient Connected | "
            f"{patient_id} | "
            f"{len(self.patient_connections[patient_id])} clients"
        )

    def disconnect_patient(
        self,
        patient_id: str,
        websocket: WebSocket,
    ):

        if patient_id not in self.patient_connections:
            return

        if websocket in self.patient_connections[patient_id]:
            self.patient_connections[patient_id].remove(websocket)

        if not self.patient_connections[patient_id]:
            del self.patient_connections[patient_id]

        print(
            f"[PATIENT DISCONNECT] Patient Disconnected | {patient_id}"
        )

    # =====================================================
    # Alerts
    # =====================================================

    async def connect_alerts(
        self,
        websocket: WebSocket,
    ):

        await websocket.accept()

        self.alert_connections.append(websocket)

        print(
            f"[ALERT CONNECT] Alert Client Connected | "
            f"{len(self.alert_connections)} clients"
        )

    def disconnect_alerts(
        self,
        websocket: WebSocket,
    ):

        if websocket in self.alert_connections:
            self.alert_connections.remove(websocket)

    # =====================================================
    # ICU Monitor
    # =====================================================

    async def connect_monitor(
        self,
        websocket: WebSocket,
    ):

        await websocket.accept()

        self.monitor_connections.append(websocket)

        print(
            f"[MONITOR CONNECT] Monitor Connected | "
            f"{len(self.monitor_connections)} clients"
        )

    def disconnect_monitor(
        self,
        websocket: WebSocket,
    ):

        if websocket in self.monitor_connections:
            self.monitor_connections.remove(websocket)

    # =====================================================
    # Send
    # =====================================================

    async def send_personal_message(
        self,
        message: dict,
        websocket: WebSocket,
    ):

        await websocket.send_text(
            json.dumps(message)
        )

    # =====================================================
    # Dashboard Broadcast
    # =====================================================

    async def broadcast(
        self,
        message: dict,
    ):
        """
        Backward compatible dashboard broadcast.
        """

        await self.broadcast_dashboard(message)

    async def broadcast_dashboard(
        self,
        message: dict,
    ):

        disconnected = []

        for connection in self.dashboard_connections:

            try:

                await connection.send_text(
                    json.dumps(message)
                )

            except Exception:

                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect_dashboard(connection)

    # =====================================================
    # Patient Broadcast
    # =====================================================

    async def broadcast_patient(
        self,
        patient_id: str,
        message: dict,
    ):

        if patient_id not in self.patient_connections:
            return

        disconnected = []

        for connection in self.patient_connections[patient_id]:

            try:

                await connection.send_text(
                    json.dumps(message)
                )

            except Exception:

                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect_patient(
                patient_id,
                connection,
            )

    # =====================================================
    # Alert Broadcast
    # =====================================================

    async def broadcast_alerts(
        self,
        message: dict,
    ):

        disconnected = []

        for connection in self.alert_connections:

            try:

                await connection.send_text(
                    json.dumps(message)
                )

            except Exception:

                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect_alerts(connection)

    # =====================================================
    # Monitor Broadcast
    # =====================================================

    async def broadcast_monitor(
        self,
        message: dict,
    ):

        disconnected = []

        for connection in self.monitor_connections:

            try:

                await connection.send_text(
                    json.dumps(message)
                )

            except Exception:

                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect_monitor(connection)

    async def ping_all(self):
        """
        Sends a heartbeat ping to all active clients and cleans up stale/dead connections.
        """
        for conn_list, disconnect_fn in [
            (self.dashboard_connections, self.disconnect_dashboard),
            (self.alert_connections, self.disconnect_alerts),
            (self.monitor_connections, self.disconnect_monitor),
        ]:
            stale = []
            for ws in list(conn_list):
                try:
                    await ws.send_json({"type": "ping"})
                except Exception:
                    stale.append(ws)
            for ws in stale:
                disconnect_fn(ws)

        for pid in list(self.patient_connections.keys()):
            stale = []
            for ws in list(self.patient_connections[pid]):
                try:
                    await ws.send_json({"type": "ping"})
                except Exception:
                    stale.append(ws)
            for ws in stale:
                self.disconnect_patient(pid, ws)

    # =====================================================
    # Statistics
    # =====================================================

    def stats(self):

        return {
            "dashboard_clients": len(
                self.dashboard_connections
            ),
            "patient_streams": len(
                self.patient_connections
            ),
            "alert_clients": len(
                self.alert_connections
            ),
            "monitor_clients": len(
                self.monitor_connections
            ),
        }


manager = ConnectionManager()