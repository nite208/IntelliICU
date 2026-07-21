"""
IntelliICU Main Application
"""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# =====================================================
# REST API Routers
# =====================================================

from app.api.dashboard import router as dashboard_router
from app.api.patients import router as patients_router
from app.api.clinical_ai import router as clinical_ai_router
from app.api.alerts import router as alerts_router
from app.api import patient_profile
from app.api.timeline_routes import router as timeline_router
from app.api.auth import router as auth_router
from app.api.rbac import router as rbac_router
from app.api.user_management import router as user_management_router, dept_router as department_router
from app.api.clinical_copilot import router as clinical_copilot_router
from app.telemetry.routes import router as telemetry_router
from app.api.hospital_assistant import router as hospital_assistant_router
from app.api.rag import router as rag_router
from app.api.ai import router as ai_router

# =====================================================
# WebSocket Routers
# =====================================================

from app.websocket.routes import router as dashboard_websocket_router
from app.websocket.patient_routes import router as patient_websocket_router

# =====================================================
# Simulator
# =====================================================

from app.websocket.simulator import simulator

# =====================================================
# Application Lifespan
# =====================================================

from app.database.session import check_db_connectivity
from app.database.seeder import seed_database_if_empty
from app.database.base import Base
from app.database.session import engine

logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup / shutdown sequence.
    Startup order: Configuration loaded -> DB validation -> Create tables -> Seed -> Init AI -> Simulator start -> Expose API.
    """
    print("=" * 60)
    print("STARTING: IntelliICU Initialization Sequence...")
    print("=" * 60)

    # 1. Database connection & validation
    db_ok = check_db_connectivity()
    if db_ok:
        # 2. Create tables
        print("DATABASE: Creating schema tables...")
        Base.metadata.create_all(bind=engine)

        # 3. Seed database
        print("DATABASE: Running seeders...")
        seed_database_if_empty()
    else:
        print("DATABASE: Connection failed. Booting in degraded/mock mode.")

    # 4. Initialize AI providers configurations
    try:
        from app.ai.factory import get_llm_provider
        provider = get_llm_provider()
        print(f"AI: Initialized provider: {provider.__class__.__name__}")
    except Exception as e:
        print(f"AI: Provider initialization warning: {e}")

    # 5. Initialize & start simulator
    print("SIMULATOR: Starting real-time telemetry simulator...")
    asyncio.create_task(simulator.start())

    # 6. Expose API
    app.state.startup_complete = True
    print("=" * 60)
    print("STARTUP COMPLETE: IntelliICU API is now accepting traffic.")
    print("=" * 60)

    yield

    print("=" * 60)
    print("SHUTDOWN: IntelliICU Shutdown")
    print("=" * 60)


# =====================================================
# FastAPI Application
# =====================================================

app = FastAPI(
    title="IntelliICU API",
    version="2.0.0",
    lifespan=lifespan,
)
app.state.startup_complete = False

# =====================================================
# Startup Protection Middleware
# =====================================================

@app.middleware("http")
async def startup_protection_middleware(request: Request, call_next):
    # Allow health checks and bootstrap endpoints prior to startup completion
    is_health_endpoint = request.url.path in ["/health", "/ready", "/live"]
    is_bootstrap = request.url.path == "/api/auth/bootstrap"
    
    if is_health_endpoint or is_bootstrap:
        return await call_next(request)

    if not getattr(app.state, "startup_complete", False):
        return JSONResponse(
            status_code=503,
            content={"detail": "Service Temporarily Unavailable: Startup initialization in progress."}
        )
    return await call_next(request)


# =====================================================
# CORS
# =====================================================

origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =====================================================
# REST APIs
# =====================================================

app.include_router(
    dashboard_router,
    prefix="/api",
)

app.include_router(
    patients_router,
    prefix="/api",
)

app.include_router(
    clinical_ai_router,
    prefix="/api",
)

app.include_router(
    alerts_router,
    prefix="/api",
)

app.include_router(
    patient_profile.router,
    prefix="/api",
)

app.include_router(
    timeline_router,
    prefix="/api",
)

app.include_router(
    auth_router,
    prefix="/api",
)

app.include_router(
    rbac_router,
    prefix="/api",
)

app.include_router(
    user_management_router,
    prefix="/api",
)

app.include_router(
    department_router,
    prefix="/api",
)

app.include_router(
    clinical_copilot_router,
    prefix="/api",
)

app.include_router(
    telemetry_router,
    prefix="/api",
)

app.include_router(
    hospital_assistant_router,
    prefix="/api",
)

app.include_router(
    rag_router,
    prefix="/api",
)

app.include_router(
    ai_router,
    prefix="/api",
)

# =====================================================
# WebSocket APIs
# =====================================================

# Dashboard Live Stream
app.include_router(
    dashboard_websocket_router,
)

# Patient Live Stream
app.include_router(
    patient_websocket_router,
)

# =====================================================
# Root & Health Endpoints
# =====================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled global exception: {str(exc)} | Path: {request.url.path}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please contact administrator."}
    )

@app.get("/health")
@app.get("/ready")
@app.get("/live")
async def health_check():
    db_ok = check_db_connectivity()
    
    # 1. Check AI Provider
    ai_ok = False
    ai_provider_name = "unknown"
    try:
        from app.ai.factory import get_llm_provider
        provider = get_llm_provider()
        if provider:
            ai_ok = True
            ai_provider_name = provider.__class__.__name__
    except Exception:
        pass

    # 2. Check Simulator
    sim_ok = False
    try:
        sim_ok = simulator is not None and len(simulator.patients) > 0
    except Exception:
        pass

    # 3. Check Telemetry Engine
    telemetry_ok = False
    try:
        from app.telemetry.trend_engine import telemetry_engine
        telemetry_ok = telemetry_engine is not None
    except Exception:
        pass

    overall_status = "healthy" if (db_ok and ai_ok and sim_ok and telemetry_ok) else "degraded"

    return {
        "status": overall_status,
        "database": "connected" if db_ok else "disconnected",
        "ai_provider": {
            "status": "online" if ai_ok else "offline",
            "name": ai_provider_name
        },
        "simulator": "running" if sim_ok else "stopped",
        "telemetry_engine": "online" if telemetry_ok else "offline",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/")
async def root():
    return {
        "application": "IntelliICU",
        "status": "running",
        "version": "2.0.0",
    }