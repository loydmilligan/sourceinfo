"""Configuration management for SourceInfo API."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API configuration settings loaded from environment."""

    # Database - default works for Docker, override with DB_PATH env var for local dev
    db_path: Path = Path("/app/data/sources.db")

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"

    # OpenRouter LLM API
    openrouter_api_key: str = ""
    default_analysis_model: str = "anthropic/claude-sonnet-4"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Counternarrative Defaults
    default_min_credibility: int = 60
    default_counternarrative_limit: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
