import os
from typing import List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with validation.
    """

    # Project Information
    PROJECT_NAME: str = "Report Card Assistant"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = ""  # Will be built from components or env var

    # Security - MUST be set via environment variables
    SECRET_KEY: str
    SESSION_SECRET_KEY: str
    SESSION_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # PostgreSQL specific
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"  # Docker service name, can be overridden
    POSTGRES_PORT: int = 5432

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if v and isinstance(v, str) and v.strip():
            return v
        # Build DATABASE_URL from components if not provided
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        host = os.getenv("POSTGRES_HOST", "db")  # Docker service name
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB")

        if not all([user, password, db]):
            raise ValueError("POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB must be set")

        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

        # Allow extra fields for forward compatibility
        extra = "allow"


# Create settings instance
settings = Settings()
