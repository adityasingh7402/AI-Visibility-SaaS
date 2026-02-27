# AI Visibility SaaS

> **Track and improve your brand's share-of-voice across every major AI-powered search engine and LLM response surface.**

AI Visibility SaaS enables marketing and SEO teams to monitor how often—and how favourably—their brand appears when users ask ChatGPT, Gemini, and Perplexity industry questions. The platform runs structured prompt experiments, scores brand citations against competitors, surfaces gap analyses, and delivers actionable recommendations to improve AI Share-of-Voice (SOV). Today the MVP is **live**: keyword management, automated prompt sampling, multi-model result capture, and a real-time dashboard are all shipped.

## Quick Links

| Document | Purpose |
|---|---|
| [PRD.md](./PRD.md) | Problem, target users, MVP scope, success metrics, milestones |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | System diagram, service responsibilities, data flow |
| [API_CONTRACTS.md](./API_CONTRACTS.md) | Request/response schemas, error codes, versioning |
| [DATA_MODEL.md](./DATA_MODEL.md) | Database tables/collections, entity definitions |
| [PROMPTING_EVALS.md](./PROMPTING_EVALS.md) | Prompt variant strategy, sampling, drift checks |
| [MODEL_PROVIDER_NOTES.md](./MODEL_PROVIDER_NOTES.md) | Per-provider capabilities, costs, quirks |
| [SECURITY_PRIVACY_COMPLIANCE.md](./SECURITY_PRIVACY_COMPLIANCE.md) | Data retention, PII, tenant isolation, ToS |
| [OPS_RUNBOOK.md](./OPS_RUNBOOK.md) | Deployment, env vars, monitoring, incident response |
| [DECISIONS.md](./DECISIONS.md) | Architecture Decision Records (ADR-lite) |

## Tech Stack

- **Frontend**: Next.js 14 (App Router)
- **Backend / API / Auth / Jobs**: Node.js (Express + BullMQ)
- **AI / Scoring / Extraction**: Python (FastAPI)
- **Database**: PostgreSQL (primary) + pgvector
- **Queue**: Redis
- **Providers**: OpenAI (ChatGPT), Google (Gemini), Perplexity

## Getting Started

```bash
# Clone the repo
git clone https://github.com/adityasingh7402/AI-Visibility-SaaS.git
cd AI-Visibility-SaaS

# See the runbook for full setup
cat OPS_RUNBOOK.md
```

## Contributing

Please read through the PRD and ARCHITECTURE docs before opening a PR. All significant decisions should be logged in DECISIONS.md.

---
*Last updated: February 2026*
