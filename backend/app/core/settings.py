from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from env vars (or a local .env). Nothing else reads os.environ."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["local", "ci", "prod"] = "local"
    app_secret_key: SecretStr = Field(min_length=32)
    log_level: str = "INFO"

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    admin_email: str | None = None
    admin_password: SecretStr | None = None

    session_max_age_s: int = 60 * 60 * 24 * 7
    login_max_attempts: int = 10
    login_window_s: int = 300

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # values come from the environment
