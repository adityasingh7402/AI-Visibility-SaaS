# ARCHITECTURE — AI Visibility SaaS

**Version:** 1.0  
**Last Updated:** 2026-02-27

---

## 1. High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                             │
│                    Next.js Frontend (UI)                        │
│   Dashboard · Run Trigger · Results · Gap View · Settings       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Node.js Service  (apps/api)                    │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Auth /  │  │ REST API │  │   Job    │  │   Storage /   │  │
│  │  JWT     │  │ Routes   │  │  Queue   │  │   File Store  │  │
│  └──────────┘  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│                     │              │                 │           │
└─────────────────────┼──────────────┼─────────────────┼──────────┘
                      │              │                 │
          ┌───────────┘   HTTP/gRPC  │                 │
          │              ┌───────────┘                 │
          ▼              ▼                             ▼
┌──────────────────────────────────┐        ┌──────────────────┐
│   Python Service  (services/py)  │        │    PostgreSQL     │
│   Owner: Pawan                   │        │   (Primary DB)   │
│                                  │        └──────────────────┘
│  ┌──────────────────────────┐    │
│  │  Prompt Builder          │    │        ┌──────────────────┐
│  │  LLM Client (3 providers)│    │        │  MongoDB (opt.)  │
│  │  Brand Mention Extractor │    │        │  Raw Fragments   │
│  │  Sentiment Scorer        │    │        └──────────────────┘
│  │  SOV Calculator          │    │
│  │  Citation Extractor      │    │        ┌──────────────────┐
│  │  Gap Analyzer            │    │        │  Redis / BullMQ  │
│  └──────────────────────────┘    │        │  Job Queue       │
└──────────────────────────────────┘        └──────────────────┘
          │
          ▼
┌──────────────────────────────────────────┐
│          External LLM Providers          │
│  OpenAI (ChatGPT)  │  Google (Gemini)    │
│  Perplexity AI     │  (future: Claude)   │
└──────────────────────────────────────────┘
```

---

## 2. Service Responsibilities

### 2.1 Next.js Frontend (`apps/web`)

| Responsibility | Notes |
|---|---|
| Authentication UI | Login, signup, JWT token storage (httpOnly cookie) |
| Workspace management | Switch/create workspaces (multi-tenant) |
| Keyword CRUD | Add, edit, delete keywords with competitor list |
| Run trigger | POST to Node API, poll for status |
| Results dashboard | SOV chart, top-1 rate, per-provider breakdown, sentiment |
| Gap analysis view | Side-by-side brand vs. competitor citation data |
| Export | CSV download of run results |

**Stack:** Next.js 14, TypeScript, Tailwind CSS, SWR for data fetching, Chart.js for visualisations.

---

### 2.2 Node.js Service (`apps/api`)

| Responsibility | Notes |
|---|---|
| **Auth & JWT** | Issue/validate JWT tokens, workspace-scoped claims |
| **REST API** | All external-facing endpoints (see API_CONTRACTS.md) |
| **Job Queue** | BullMQ backed by Redis; enqueues run jobs, manages retries |
| **Orchestration** | Calls Python service with run payload, awaits results |
| **Storage layer** | Writes/reads Run, ModelResult, Fragment records to Postgres |
| **File store** | Stores raw LLM response JSON blobs (S3 or local disk) |
| **Tenant isolation** | Every DB query scoped by `workspace_id` |
| **Rate limit proxy** | Queue-aware rate limiting per provider |

**Stack:** Node.js 20, Express, TypeScript, BullMQ, Prisma ORM, JWT, Zod validation.

---

### 2.3 Python Service (`services/python`) — Owner: Pawan

| Responsibility | Notes |
|---|---|
| **Prompt Builder** | Generates N variants per keyword using templated strategies |
| **LLM Client** | Calls ChatGPT, Gemini, Perplexity APIs; handles auth, retries |
| **Brand Mention Extractor** | Finds brand + alias occurrences in response text |
| **Sentiment Scorer** | classifies mention context (positive / neutral / negative) |
| **SOV Calculator** | Aggregates mention flags into SOV % and Top-1 rate |
| **Citation Extractor** | Pulls URLs from Perplexity citations, source cards from Gemini |
| **Gap Analyzer** | Compares brand vs. competitor mention vectors; returns gap report |
| **Embedding Store** | Optionally stores response embeddings for drift checks |

**Stack:** Python 3.11, FastAPI, OpenAI SDK, Google GenAI SDK, Perplexity SDK, spaCy / sentence-transformers, pandas, SQLAlchemy.

---

## 3. Data Flow

```
1. USER enters keyword + competitors in UI
   └─► Next.js sends POST /visibility/run to Node API

2. Node API validates, creates Run record (status=QUEUED)
   └─► Enqueues job on BullMQ

3. BullMQ worker picks job
   └─► Node calls POST /internal/run on Python service

4. Python service:
   a. Prompt Builder → generates N prompt variants
   b. LLM Client → calls ChatGPT, Gemini, Perplexity in parallel
   c. Brand Mention Extractor → scans each response
   d. Sentiment Scorer → classifies each mention
   e. Citation Extractor → pulls source URLs
   f. SOV Calculator → computes SOV %, Top-1 rate per provider
   g. Returns structured JSON result payload

5. Node API receives payload
   └─► Writes ModelResult rows to Postgres
   └─► Writes raw response blobs to file store
   └─► Updates Run status = COMPLETED

6. Next.js UI polls GET /runs/:id
   └─► Displays results dashboard when status = COMPLETED

7. (Optional) User triggers Gap Analysis
   └─► Next.js sends POST /gap/run
   └─► Node calls Python gap analyzer
   └─► Returns brand vs. competitor gap report
```

---

## 4. Deployment Topology (MVP)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Vercel      │     │  Railway /   │     │  Railway /   │
│  (Next.js)   │────▶│  Render      │────▶│  Render      │
│              │     │  (Node API)  │     │  (Python Svc)│
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                  ┌─────────┼──────────┐
                  ▼         ▼          ▼
            Postgres      Redis      S3/R2
           (Supabase)  (Upstash)  (Cloudflare)
```

All services communicate over private network or authenticated HTTPS.  
See [OPS_RUNBOOK.md](./OPS_RUNBOOK.md) for environment variables and secrets management.
