# MODEL PROVIDER NOTES — AI Visibility SaaS

**Owner:** Pawan (Python service integration)  
**Last Updated:** 2026-02-27

---

## Overview

This document covers provider-specific implementation details for the three LLM providers integrated in the MVP. Each section covers capabilities, citation availability, cost, rate limits, quirks, and recommended settings.

---

## 1. ChatGPT (OpenAI)

### Capabilities

| Capability | Status |
|---|---|
| Text completion | ✅ |
| JSON mode (`response_format`) | ✅ |
| Streaming | ✅ (not used in MVP) |
| System prompt | ✅ |
| Citations / source URLs | ❌ (model knowledge only) |
| Web search / retrieval | ✅ via `gpt-4o` with browsing (opt-in) |
| Seed for reproducibility | ✅ (`seed` parameter) |

### Models Used

| Model | Use Case | Notes |
|---|---|---|
| `gpt-4o` | Primary visibility runs | Best quality, higher cost |
| `gpt-4o-mini` | High-volume / cost-efficiency runs | 90% quality, 10x cheaper |

### Cost (Approximate)

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Typical run cost (N=10, ~500 tokens/prompt) |
|---|---|---|---|
| `gpt-4o` | $5 | $15 | ~$0.05 |
| `gpt-4o-mini` | $0.15 | $0.60 | ~$0.002 |

### Rate Limits (Tier 2)

| Limit | Value |
|---|---|
| RPM | 5,000 |
| TPM | 450,000 |
| Max prompt tokens | 128,000 |

### Quirks & Gotchas

- **No live citations:** responses are from training data — cannot retrieve live source URLs.
- **Seed is a hint, not a guarantee:** same seed may produce slightly different outputs across API versions.
- **JSON mode requires mention of JSON in system prompt**, otherwise API may return 400.
- **Rate limit headers:** `x-ratelimit-remaining-requests`, `x-ratelimit-reset-requests` — use these for adaptive throttling.

### Recommended Settings (Visibility Runs)

```python
{
    "model": "gpt-4o",
    "temperature": 0.2,
    "top_p": 0.9,
    "max_tokens": 800,
    "seed": hash(run_id) % (2**32),
    "response_format": { "type": "json_object" },
    "messages": [
        { "role": "system", "content": SYSTEM_PROMPT_JSON_EXTRACTION },
        { "role": "user", "content": prompt_text }
    ]
}
```

---

## 2. Gemini (Google)

### Capabilities

| Capability | Status |
|---|---|
| Text completion | ✅ |
| JSON mode (`response_mime_type`) | ✅ |
| Streaming | ✅ (not used in MVP) |
| System prompt (`system_instruction`) | ✅ |
| Citations / source URLs | ⚠️ Partial (Grounding API — separate) |
| Web grounding | ✅ via Google Search Grounding (additional cost) |
| Seed for reproducibility | ❌ Not supported |

### Models Used

| Model | Use Case |
|---|---|
| `gemini-1.5-pro` | Primary visibility runs |
| `gemini-1.5-flash` | High-volume / cost-efficiency |

### Cost (Approximate)

| Model | Input | Output | Typical run cost (N=10) |
|---|---|---|---|
| `gemini-1.5-pro` | $3.50/1M | $10.50/1M | ~$0.035 |
| `gemini-1.5-flash` | $0.075/1M | $0.30/1M | ~$0.0015 |

### Rate Limits (Pay-as-you-go)

| Limit | `gemini-1.5-pro` | `gemini-1.5-flash` |
|---|---|---|
| RPM | 360 | 1,000 |
| TPM | 4,000,000 | 4,000,000 |

### Quirks & Gotchas

- **JSON mode requires schema-like system prompt** — be explicit about output structure.
- **No seed parameter** — responses are inherently non-deterministic; expect higher variance than OpenAI.
- **Grounding API is separate** — web-sourced responses cost extra (~$35/1,000 queries); not used in MVP by default.
- **Safety filters** — Gemini may refuse or heavily modify responses on competitive brand comparison prompts. Use mitigation: frame as informational rather than evaluative.
- **`finish_reason: SAFETY`** — handle this case explicitly; log and mark result as `FILTERED`.

### Recommended Settings

```python
generation_config = {
    "temperature": 0.2,
    "top_p": 0.9,
    "max_output_tokens": 800,
    "response_mime_type": "application/json",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    system_instruction=SYSTEM_PROMPT_JSON_EXTRACTION,
    generation_config=generation_config,
)
```

---

## 3. Perplexity AI

### Capabilities

| Capability | Status |
|---|---|
| Text completion | ✅ |
| JSON mode | ❌ (no native support) |
| Streaming | ✅ (not used in MVP) |
| System prompt | ✅ |
| Citations / source URLs | ✅ **Strong** — returns structured `citations` array |
| Web search / retrieval | ✅ Built-in (always on for `sonar` models) |
| Seed for reproducibility | ❌ |

### Models Used

| Model | Use Case |
|---|---|
| `llama-3.1-sonar-large-128k-online` | Primary (citations + quality) |
| `llama-3.1-sonar-small-128k-online` | Cost-efficient |

### Cost (Approximate)

| Model | Cost per 1M tokens | Typical run cost (N=10) |
|---|---|---|
| `sonar-large` | $1.00 in / $1.00 out + $5/1k search | ~$0.06 |
| `sonar-small` | $0.20 in / $0.20 out + $5/1k search | ~$0.02 |

### Rate Limits

| Limit | Value |
|---|---|
| RPM | 50 (free) / 200 (paid) |
| Concurrent requests | 10 |

**Important:** Perplexity has relatively low RPM limits — queue requests with delay between batches.

### Quirks & Gotchas

- **Citations are the main differentiator** — always extract and store the `citations` array (URLs + titles).
- **No JSON mode** — must parse free-text response; use regex fallback + GPT-3.5 extraction on failure.
- **Search is always on** — responses reflect live web state, not training data. This means results can change more run-to-run than OpenAI/Gemini.
- **Low RPM** — at N=10 with 3 providers, Perplexity is often the bottleneck. Implement per-provider queue with rate limit tracking.
- **Follow-up context** — Perplexity performs best with single-turn, self-contained prompts. Avoid multi-turn.

### Recommended Settings

```python
response = client.chat.completions.create(
    model="llama-3.1-sonar-large-128k-online",
    messages=[
        { "role": "system", "content": SYSTEM_PROMPT_PLAIN },
        { "role": "user", "content": prompt_text }
    ],
    temperature=0.2,
    max_tokens=800,
)
# Extract citations:
citations = response.citations  # list of URLs
```

---

## 4. Future Providers (Post-MVP)

| Provider | Priority | Notes |
|---|---|---|
| Claude (Anthropic) | High | Strong reasoning, growing market share in AI search |
| Google AI Overviews / SGE | High | Requires scraping or partner API access — legal review needed |
| Microsoft Copilot / Bing AI | Medium | Via Bing Chat API or Azure OpenAI |
| You.com | Low | Niche but citation-heavy |

---

## 5. Provider Comparison Summary

| Feature | ChatGPT | Gemini | Perplexity |
|---|---|---|---|
| Citations | ❌ | ⚠️ Grounding add-on | ✅ Built-in |
| JSON Mode | ✅ | ✅ | ❌ |
| Seed/Determinism | ✅ | ❌ | ❌ |
| Live Web Data | Opt-in | Opt-in | ✅ Always |
| Cost (N=10 run) | ~$0.05 | ~$0.035 | ~$0.06 |
| Rate Limits | Generous | Generous | Restrictive |
| Safety Filtering | Low | Medium | Low |
