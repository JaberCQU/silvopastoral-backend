# ============================================================
# CQ Silvopastoral Dashboard -- Backend Configuration
# ============================================================
# All settings are read from environment variables (or a local
# .env file when running locally). Nothing sensitive is hardcoded
# here -- this file only defines WHAT settings exist, not their
# values, so it is always safe to commit to GitHub.
#
# Required environment variables in production (Render/Railway):
#   DATABASE_URL        -- provided automatically by the platform
#                           when you attach a PostgreSQL database
#   SECRET_KEY           -- a long random string for signing JWTs
#   ALLOWED_ORIGINS       -- comma-separated list of frontend URLs
#                           allowed to call this API (CORS)
# ============================================================

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # -- Database --
    # Falls back to a local SQLite file if DATABASE_URL is not set,
    # so the API can be run and tested without installing Postgres.
    database_url: str = "sqlite:///./silvopastoral.db"

    # -- Auth / JWT --
    secret_key: str = "dev-only-insecure-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # -- CORS --
    # Comma-separated string of allowed frontend origins, e.g.
    # "https://jabercqu.github.io,http://localhost:5500"
    allowed_origins: str = "http://localhost:5500,http://127.0.0.1:5500"

    class Config:
        env_file = ".env"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance -- reads env vars once per process."""
    return Settings()
