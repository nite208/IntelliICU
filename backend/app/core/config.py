"""
Application configuration for IntelliICU.

Centralizes environment-specific settings using Pydantic Settings.
Supports both Local PostgreSQL and Production (Neon/Render).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # ---------------------------------------------------------
    # Project
    # ---------------------------------------------------------

    PROJECT_NAME: str = "IntelliICU Backend"

    PROJECT_DESCRIPTION: str = (
        "Enterprise AI Clinical Decision Support Platform "
        "for Intensive Care Units."
    )

    PROJECT_VERSION: str = "1.0.0"

    API_V1_PREFIX: str = "/api/v1"

    DEBUG: bool = True

    # ---------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------

    AUTH_SECRET_KEY: str = "intelliicu_super_secret_key_change_me_in_production"
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------

    # Production (Render / Neon)
    DATABASE_URL: str | None = None

    # Local PostgreSQL
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5433
    DATABASE_NAME: str = "intelliicu"
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "YOUR_PASSWORD"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Returns the correct SQLAlchemy connection string.

        Priority:
        1. DATABASE_URL (Production)
        2. Local PostgreSQL credentials
        """

        if self.DATABASE_URL:
            url = self.DATABASE_URL

            # Render/Neon may provide postgres://
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg://", 1)

            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)

            return url

        # Local Development
        return (
            f"postgresql+psycopg://"
            f"{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"
        )

    # Backward compatibility
    @property
    def DATABASE_CONNECTION(self) -> str:
        return self.SQLALCHEMY_DATABASE_URI

    @property
    def DATABASE_URI(self) -> str:
        return self.SQLALCHEMY_DATABASE_URI

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()