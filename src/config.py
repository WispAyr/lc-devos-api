"""Application configuration using Pydantic settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    db_user: str = "devos"
    db_password: str = "devos"
    db_host: str = "127.0.0.1"
    db_port: int = 5432
    db_name: str = "devos"

    # API
    api_port: int = 3001
    secret_key: str = "change_me_in_production_or_local_setup"

    # Runner
    runner_id: str = "local-mac-01"

    # Redis
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def database_url_sync(self) -> str:
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
