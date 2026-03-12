"""
GEO Platform — App Configuration
Type-safe environment config using Pydantic Settings.
Dual Groq API keys for rate-limit management.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central config — all values from .env or environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    app_env: str = "development"
    app_debug: bool = False
    log_level: str = "INFO"

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    hmac_secret_key: str = "dev-secret-change-me"

    # --- Groq (Internal LLM — dual keys) ---
    groq_api_key_1: str = ""
    groq_api_key_2: str = ""

    # --- Fallback Providers ---
    fireworks_api_key: str = ""
    mistral_api_key: str = ""

    # --- Google (Vision + emergency fallback) ---
    google_api_key: str = ""

    # --- Customer LLM Providers (Agent 3) ---
    openai_api_key: str = ""
    xai_api_key: str = ""
    anthropic_api_key: str = ""
    perplexity_api_key: str = ""

    # --- Search APIs ---
    tavily_api_key: str = ""
    google_cse_api_key: str = ""
    google_cse_engine_id: str = ""

    # --- LangFuse Observability ---
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    # --- Timeouts (seconds) ---
    crawler_timeout: int = 10
    researcher_timeout: int = 30
    llm_tester_timeout: int = 30
    image_analyzer_timeout: int = 20
    optimizer_timeout: int = 30
    verifier_timeout: int = 10
    total_pipeline_timeout: int = 90

    # --- Quality ---
    multi_run_count: int = Field(default=5, description="Times each prompt is tested")
    max_verifier_retries: int = Field(default=2, description="Agent 5↔6 retry cap")

    @property
    def is_dev(self) -> bool:
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Cached settings — loaded once, reused everywhere."""
    return Settings()
