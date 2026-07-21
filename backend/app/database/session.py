import logging

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger("app.database")

# ==========================================================
# Database Engine Configuration
# ==========================================================

connect_args = {}
engine_kwargs = {}

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# PostgreSQL / Neon Configuration
if not DATABASE_URL.startswith("sqlite"):

    connect_args = {
        "connect_timeout": 10,
    }

    engine_kwargs = {
        "connect_args": connect_args,

        # Connection Pool
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_use_lifo": True,

        # SQLAlchemy 2.x
        "future": True,
    }

# SQLite Configuration (Local Development)
else:

    engine_kwargs = {
        "connect_args": {
            "check_same_thread": False,
        },
        "future": True,
    }

# ==========================================================
# Engine
# ==========================================================

engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    **engine_kwargs,
)

# ==========================================================
# Session Factory
# ==========================================================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

# ==========================================================
# Dependency
# ==========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================================
# Health Check
# ==========================================================

def check_db_connectivity() -> bool:
    """
    Verify database connectivity.

    Returns:
        True  -> Database reachable
        False -> Database unavailable
    """

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Database connectivity verified successfully.")
        return True

    except OperationalError as exc:
        logger.warning(
            "Database not reachable during startup. "
            "The application will continue and retry later. "
            "Details: %s",
            exc,
        )
        return False

    except Exception as exc:
        logger.exception(
            "Unexpected database connectivity error: %s",
            exc,
        )
        return False