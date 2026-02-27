# AI Visibility SaaS

> **Track and improve your brand's presence across AI-powered search engines and LLM responses.**

AI Visibility SaaS is a multi-tenant platform that lets marketing teams, SEO professionals, and brand managers measure how often — and how positively — their brand appears when real users ask AI assistants (ChatGPT, Gemini, Perplexity) questions in their category. The platform runs structured prompt campaigns, scores each response for brand mention, sentiment, and citation quality, surfaces gap analyses against top competitors, and surfaces actionable recommendations to improve Share-of-Voice (SOV) inside generative AI responses.

## Who It's For

| Persona | Pain Point Solved |
|---|---|
| Brand / Growth Marketers | "Are we even showing up in AI answers for our category?" |
| SEO / GEO Specialists | "How do we optimise content to get cited by LLMs?" |
| Product & Strategy | "Which competitor is winning the AI channel, and why?" |
| Agency Clients | "Show me a dashboard I can share with my CMO." |

## What's Shipped (MVP)

- ✅ Keyword → prompt campaign runner (ChatGPT, Gemini, Perplexity)
- ✅ Brand mention detection + sentiment scorer (Python service)
- ✅ Share-of-Voice (SOV) and Top-1 ranking metrics
- ✅ Gap analyzer comparing brand vs. competitor citation patterns
- ✅ Run history storage (Postgres) with per-run drill-down UI
- ✅ Next.js dashboard with auth (JWT) and multi-tenant workspace isolation
- ✅ REST API for all core operations

## Quick Links

| Doc | Description |
|---|---|
| [PRD.md](./PRD.md) | Problem, MVP scope, success metrics, milestones |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System diagram, service responsibilities, data flow |
| [API_CONTRACTS.md](./API_CONTRACTS.md) | Request/response schemas, error codes, versioning |
| [DATA_MODEL.md](./DATA_MODEL.md) | Database entities and schema |
| [PROMPTING_EVALS.md](./PROMPTING_EVALS.md) | Prompt strategy, sampling, evaluation |
| [MODEL_PROVIDER_NOTES.md](./MODEL_PROVIDER_NOTES.md) | Per-provider quirks, costs, rate limits |
| [SECURITY_PRIVACY_COMPLIANCE.md](./SECURITY_PRIVACY_COMPLIANCE.md) | Data retention, PII, tenant isolation |
| [OPS_RUNBOOK.md](./OPS_RUNBOOK.md) | Deployment, env vars, monitoring, incident response |
| [DECISIONS.md](./DECISIONS.md) | Architecture Decision Records (ADR-lite) |

## Tech Stack (TL;DR)

```
Next.js (UI)  →  Node.js API/Orchestration  →  Python LLM Service (Pawan)
                        ↓
                   Postgres (primary storage)
```

## Getting Started

```bash
# Clone
git clone https://github.com/adityasingh7402/AI-Visibility-SaaS.git
cd AI-Visibility-SaaS

# Install all services
cd apps/web && npm install
cd ../api && npm install
cd ../../services/python && pip install -r requirements.txt

# Copy env files
cp .env.example .env

# Run (dev)
docker-compose up
```

See [OPS_RUNBOOK.md](./OPS_RUNBOOK.md) for full environment variable reference and production deployment steps.

---

*Last updated: 2026-02-27*
