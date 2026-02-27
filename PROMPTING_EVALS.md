# PROMPTING & EVALS — AI Visibility SaaS

**Owner:** Pawan (Python service)  
**Last Updated:** 2026-02-27

---

## 1. Prompt Variant Strategy

The goal is to simulate *real user behaviour* — not one canonical prompt, but the **distribution of natural-language ways** a user might ask a question in a category.

### 1.1 Variant Dimensions

For each keyword (e.g. `"best CRM for startups"`), we generate variants along these axes:

| Dimension | Examples |
|---|---|
| **Framing** | question / imperative / conversational statement |
| **Persona** | "I'm a startup founder", "As an SMB marketer", "My team needs..." |
| **Specificity** | generic / feature-specific / use-case-specific |
| **Tone** | neutral / urgent ("I need to choose today") / evaluative ("compare for me") |
| **Length** | short (5–8 words) / medium (10–18 words) / long (20+ words) |

### 1.2 Template Library

Templates are stored in `services/python/prompts/templates/`. Each template has:

```yaml
id: "tmpl_q_neutral_001"
framing: question
persona: null
tone: neutral
length: medium
template: "What are the best {category} options for {audience}?"
```

### 1.3 Variant Generation Algorithm

```python
def generate_variants(keyword: Keyword, n: int = 10) -> list[str]:
    templates = load_templates()
    selected = sample_templates(templates, n, strategy="stratified")
    return [
        render_template(t, keyword)
        for t in selected
    ]
```

**Stratified sampling** ensures coverage across all dimension combinations.  
**Deterministic seeding:** the run's `runId` (hashed) is used as the random seed — so re-running the same job with the same seed produces the same prompt set. This supports reproducibility for regression testing.

---

## 2. N — Sample Size Recommendations

| N (variants) | Cost (est. 3 providers) | Confidence Interval (SOV) | Recommended Use |
|---|---|---|---|
| 5 | ~$0.04 | ±12% | Quick spot-check |
| 10 | ~$0.08 | ±8% | **Default (MVP)** |
| 20 | ~$0.16 | ±6% | Weekly scheduled runs |
| 50 | ~$0.40 | ±4% | Deep audit / benchmarking |

SOV confidence intervals based on binomial proportion (95% CI, p=0.5 worst case).

---

## 3. Determinism Controls

LLMs are non-deterministic by default. We apply these controls to reduce variance:

| Control | ChatGPT | Gemini | Perplexity |
|---|---|---|---|
| `temperature` | 0.2 | 0.2 | N/A (no control) |
| `top_p` | 0.9 | 0.9 | N/A |
| `seed` | set to hash(runId) | not supported | N/A |
| Repeat each prompt | 1x (MVP) | 1x (MVP) | 1x (MVP) |

> **Note:** Even with controls, response variance exists, especially on Perplexity. Treat SOV as a statistical estimate, not a deterministic count.

---

## 4. JSON Enforcement

For structured extraction, we use **JSON mode** where available:

| Provider | JSON Mode |
|---|---|
| ChatGPT | `response_format: { type: "json_object" }` |
| Gemini | `response_mime_type: "application/json"` |
| Perplexity | Not natively supported — post-process with regex + fallback parser |

**Fallback strategy:**
1. Try JSON parse
2. If fails, regex extract JSON block from markdown code fence
3. If fails, run response through secondary extraction model (GPT-3.5-turbo)
4. If fails, mark result as `PARSE_ERROR`, store raw, continue

---

## 5. Evaluation Set

We maintain a **golden eval dataset** in `services/python/evals/golden_set.jsonl`.

### 5.1 Dataset Structure

```jsonl
{
  "prompt": "What CRM should I use for my SaaS startup?",
  "response": "For SaaS startups, HubSpot and Salesforce are the most frequently...",
  "expected_brand_mentioned": true,
  "expected_brand": "HubSpot",
  "expected_sentiment": "positive",
  "expected_is_top1": true
}
```

### 5.2 Eval Metrics (Extraction)

| Metric | Target | Current |
|---|---|---|
| Brand Mention Detection F1 | > 0.92 | 0.94 |
| Top-1 Accuracy | > 0.90 | 0.91 |
| Sentiment Accuracy | > 0.85 | 0.87 |
| JSON Parse Success Rate | > 0.98 | 0.99 |

Run evals with:

```bash
cd services/python
python -m evals.run_evals --dataset evals/golden_set.jsonl --report
```

### 5.3 Eval Cadence

| Event | Action |
|---|---|
| Pre-release (any Python service deploy) | Run full eval suite; block deploy if F1 drops > 2% |
| Weekly | Automated eval run; alert on Slack if degradation detected |
| New provider added | Extend eval dataset with 50+ new provider-specific samples |

---

## 6. Drift Checks

Prompt effectiveness and LLM behaviour can drift over time.

### 6.1 SOV Drift Alert

- **Trigger:** SOV for a tracked keyword drops > 15% week-over-week
- **Action:** Flag for manual review; optionally send webhook notification to customer

### 6.2 Embedding Drift (Optional)

- Store embeddings of LLM responses per run (`embedding_refs` table)
- Weekly: compute cosine similarity between current and previous week's response embeddings
- If avg similarity < 0.85: flag potential model update by provider

### 6.3 Response Length Drift

- Track `avg_completion_tokens` per provider per week
- Alert if changes > 30% — may indicate silently changed model or system prompt
