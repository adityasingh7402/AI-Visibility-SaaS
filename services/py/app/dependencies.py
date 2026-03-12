"""
GEO Platform — Dependency Injection
Shared resources loaded once and injected into routes/agents.
"""

from functools import lru_cache
from pathlib import Path

import yaml
import structlog

from app.config import Settings, get_settings

log = structlog.get_logger()

# Registry file path (relative to services/py/)
REGISTRY_PATH = Path(__file__).parent.parent / "providers_registry.yaml"


@lru_cache
def get_provider_registry() -> dict:
    """Load provider registry YAML — cached after first load."""
    with open(REGISTRY_PATH) as f:
        data = yaml.safe_load(f)

    providers = data.get("providers", {})
    log.info("provider_registry_loaded", count=len(providers))
    return providers


def get_default_model(provider_id: str) -> str | None:
    """Get the default model ID for a given provider.

    Returns None if provider not found.
    """
    registry = get_provider_registry()
    provider = registry.get(provider_id)
    if not provider:
        return None

    for model in provider.get("available_models", []):
        if model.get("is_default"):
            return model["id"]

    # Fallback: return first model
    models = provider.get("available_models", [])
    return models[0]["id"] if models else None


def get_litellm_model_id(provider_id: str, model_id: str) -> str:
    """Convert registry IDs to LiteLLM format.

    Example: ('chatgpt', 'gpt-4o') → 'openai/gpt-4o'
    """
    registry = get_provider_registry()
    provider = registry.get(provider_id, {})
    prefix = provider.get("litellm_prefix", provider_id)
    return f"{prefix}/{model_id}"


def get_api_key_for_provider(provider_id: str, settings: Settings | None = None) -> str:
    """Look up the API key for a customer-selected provider."""
    settings = settings or get_settings()
    registry = get_provider_registry()
    provider = registry.get(provider_id, {})
    env_key = provider.get("env_key", "")

    # Map env_key name to settings attribute
    key_mapping = {
        "OPENAI_API_KEY": settings.openai_api_key,
        "GOOGLE_API_KEY": settings.google_api_key,
        "XAI_API_KEY": settings.xai_api_key,
        "ANTHROPIC_API_KEY": settings.anthropic_api_key,
        "PERPLEXITY_API_KEY": settings.perplexity_api_key,
    }
    return key_mapping.get(env_key, "")
