"""
GEO Platform — Multi-Provider LLM Fallback Chain
Routes LLM calls through a priority-ordered chain of providers.
Switches to next provider on failure in <500ms.

Chain: Groq → Fireworks → Groq(8B) → Mistral API → Google
"""

import time

import litellm
import structlog

from app.config import get_settings

log = structlog.get_logger()

# Suppress LiteLLM's verbose logging
litellm.suppress_debug_info = True


# --- Fallback Chain Definition ---
# Multi-provider: same model on different providers = true resilience
FALLBACK_CHAIN = [
    {
        "model": "groq/llama-3.3-70b-versatile",
        "label": "Llama 70B / Groq",
        "tier": "primary",
    },
    {
        "model": "fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct",
        "label": "Llama 70B / Fireworks",
        "tier": "fallback",
    },
    {
        "model": "groq/llama-3.1-8b-instant",
        "label": "Llama 8B / Groq",
        "tier": "fast",
    },
    {
        "model": "mistral/mistral-large-latest",
        "label": "Mistral Large / Mistral API",
        "tier": "fallback",
    },
    {
        "model": "gemini/gemini-2.0-flash",
        "label": "Gemini Flash / Google",
        "tier": "emergency",
    },
]


def _get_api_key_for_model(model: str, agent_group: str = "research") -> str | None:
    """Route the correct API key based on model provider and agent group.

    Agent groups:
      'research' → Groq Key 1 (Agents 1, 2)
      'optimize' → Groq Key 2 (Agents 5, 6)
    """
    settings = get_settings()

    if "groq/" in model:
        return settings.groq_api_key_1 if agent_group == "research" else settings.groq_api_key_2
    elif "fireworks" in model:
        return settings.fireworks_api_key
    elif "mistral/" in model:
        return settings.mistral_api_key
    elif "gemini/" in model:
        return settings.google_api_key
    return None


async def llm_call(
    messages: list[dict],
    agent_group: str = "research",
    response_model=None,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> object:
    """Call LLM with automatic fallback chain.

    Steps:
      1. Try each model in FALLBACK_CHAIN order
      2. On failure, log and switch to next (<500ms)
      3. If using instructor, return structured Pydantic model
      4. If all fail, raise last exception

    Args:
        messages: Chat messages for the LLM.
        agent_group: 'research' or 'optimize' — picks Groq API key.
        response_model: Optional Pydantic model for structured output (via instructor).
        temperature: LLM temperature.
        max_tokens: Max tokens in response.
    """
    last_error = None

    for provider in FALLBACK_CHAIN:
        model = provider["model"]
        label = provider["label"]
        api_key = _get_api_key_for_model(model, agent_group)

        # Skip providers with no API key configured
        if not api_key:
            continue

        start = time.perf_counter()

        try:
            # Step 1: Build call arguments
            call_kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "api_key": api_key,
                "timeout": 30,
            }

            # Step 2: Use instructor for structured output, or raw LiteLLM
            if response_model:
                import instructor
                client = instructor.from_litellm(litellm.acompletion)
                result = await client.chat.completions.create(
                    response_model=response_model,
                    **call_kwargs,
                )
            else:
                result = await litellm.acompletion(**call_kwargs)

            # Step 3: Log success
            elapsed_ms = (time.perf_counter() - start) * 1000
            log.info(
                "llm_call_success",
                provider=label,
                elapsed_ms=round(elapsed_ms),
                agent_group=agent_group,
            )
            return result

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            last_error = e

            log.warning(
                "llm_call_failed_switching",
                provider=label,
                error=str(e)[:200],
                elapsed_ms=round(elapsed_ms),
                agent_group=agent_group,
            )
            continue

    # All providers exhausted
    log.error("llm_fallback_chain_exhausted", last_error=str(last_error)[:200])
    raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")
