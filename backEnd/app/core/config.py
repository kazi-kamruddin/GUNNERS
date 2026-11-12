from typing import Annotated, Any, List
import json
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:4173",
]


def _parse_origins(value: Any) -> List[str]:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        return [item.strip() for item in stripped.split(",") if item.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return list(_DEFAULT_ORIGINS)


class Settings(BaseSettings):
    PROJECT_NAME: str = "GUNNERS Reborn API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    TESTING: bool = False

    # CORS
    ALLOWED_ORIGINS: Annotated[List[str], NoDecode] = list(_DEFAULT_ORIGINS)
    BACKEND_CORS_ORIGINS: Annotated[List[str], NoDecode] = list(_DEFAULT_ORIGINS)

    # Database (Supabase PostgreSQL via PgBouncer or local SQLite for testing fallback)
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # Supabase Auth
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Football Data Provider API
    FOOTBALL_DATA_API_KEY: str = ""

    @field_validator("ALLOWED_ORIGINS", "BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        return _parse_origins(v)

    @model_validator(mode="after")
    def sync_cors_origins(self) -> "Settings":
        # Keep ALLOWED_ORIGINS and BACKEND_CORS_ORIGINS synchronized cleanly.
        fields_set = self.model_fields_set
        if "ALLOWED_ORIGINS" in fields_set and "BACKEND_CORS_ORIGINS" not in fields_set:
            base = list(self.ALLOWED_ORIGINS)
        elif "BACKEND_CORS_ORIGINS" in fields_set and "ALLOWED_ORIGINS" not in fields_set:
            base = list(self.BACKEND_CORS_ORIGINS)
        else:
            base = list(self.ALLOWED_ORIGINS) + list(self.BACKEND_CORS_ORIGINS)

        merged: List[str] = []
        for origin in base:
            if origin not in merged:
                merged.append(origin)
        if self.ENVIRONMENT != "production":
            for dev_origin in ("http://localhost:5173", "http://localhost:4173"):
                if dev_origin not in merged:
                    merged.append(dev_origin)
        self.ALLOWED_ORIGINS = merged
        self.BACKEND_CORS_ORIGINS = merged
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
