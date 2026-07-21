"""
app/telemetry/__init__.py

Enterprise Telemetry Trend Engine Package.

Exposes the singleton TelemetryEngine instance and the FastAPI router.
External callers should only import from here — never directly from sub-modules.
"""

from app.telemetry.trend_engine import TelemetryEngine, telemetry_engine
from app.telemetry.routes import router as telemetry_router

__all__ = ["TelemetryEngine", "telemetry_engine", "telemetry_router"]
