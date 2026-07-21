"""
Application factory for the IntelliICU backend.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from app.api.router import router as api_router
from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.core.exceptions import register_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Manage the application startup and shutdown lifecycle.

    Args:
        app: FastAPI application instance.
    """
    configure_logging()
    logger.info(
    "Application startup",
    application="IntelliICU Backend",
)

    yield

    logger.info(
    "Application shutdown",
    application="IntelliICU Backend",
)


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """

    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        )

    application.include_router(api_router)
    register_exception_handlers(application)

    return application