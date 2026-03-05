# CONTRIBUTORS — AI Visibility SaaS

**Last Updated:** 2026-03-05
**Version:** 1.0

This document defines the three core developers, their exact responsibilities, the areas of the codebase and documentation they own, and collaboration rules across the team.

---

## 1. Team Overview

| Developer | Role | Primary Focus |
|---|---|---|
| **Aditya Singh** | Full-Stack Engineer & Project Lead | Dashboard, website UI interactivity, Node.js API, database, auth, infrastructure, deployment |
| **Indranil** | Frontend Designer & Marketing Engineer | Design system, UI/UX aesthetics, branding, marketing pages, visual polish |
| **Pawan** | AI/ML Engineer | Python LLM service, prompt engine, brand extraction, scoring, gap analysis, evals |

---

## 2. Developer Profiles

---

### 🧑‍💻 Aditya Singh — Full-Stack Engineer & Project Lead

**GitHub:** [@adityasingh7402](https://github.com/adityasingh7402)

#### Core Responsibilities

| Area | Details |
|---|---|
| **Next.js Dashboard** | All user-facing app pages — login, signup, workspace dashboard, run trigger UI, results views, gap analysis view, settings, CSV export |
| **Node.js REST API** | All API endpoints (`/visibility/run`, `/runs`, `/gap/run`, etc.), request validation (Zod), response formatting |
| **Job Queue** | BullMQ workers on Redis, job retry logic, run orchestration, Python service callback handling |
| **Database** | PostgreSQL schema design, Prisma ORM, migrations, indexes, multi-tenant query enforcement |
| **Auth System** | JWT access + refresh token flow, RS256 signing, RBAC middleware, httpOnly cookie management |
| **Infrastructure** | Docker, Vercel (Next.js), Railway/Render (API), Supabase (DB), Upstash (Redis), Cloudflare R2 (blobs) |
| **Monitoring & Ops** | Sentry, uptime alerts, incident response, backup management, cost controls at workspace level |
| **Project Lead** | Architecture decisions, documentation ownership, release management, PR reviews |

#### Codebase Ownership

```
apps/
  web/                          → Aditya (Next.js UI — except design files, see Indranil)
    app/(dashboard)/            → Aditya (run trigger, results, gap view, settings)
    app/(auth)/                 → Aditya (login, signup, session)
    lib/                        → Aditya (API client, hooks, state)
  api/                          → Aditya (100%)
    src/
      routes/                   → Aditya
      middleware/tenantScope.ts → Aditya
      queues/                   → Aditya
      auth/                     → Aditya
      storage/                  → Aditya (R2 blob upload/download)
```

#### Documentation Sections Owned

| Document | Sections |
|---|---|
| `README.md` | Entire file |
| `PRD.md` | Entire file (project lead), UI/dashboard MVP scope items |
| `ARCHITECTURE.md` | Sections 2.1 (Next.js), 2.2 (Node.js), 3 (data flow), 4 (deployment) |
| `API_CONTRACTS.md` | Entire file — all endpoint design and implementation |
| `DATA_MODEL.md` | workspaces, users, keywords, runs, prompt_variants tables; Prisma ORM layer |
| `DECISIONS.md` | ADR-001, ADR-002, ADR-003, ADR-004, ADR-006, ADR-007, ADR-008 |
| `OPS_RUNBOOK.md` | Sections 2.1, 2.2, 3, 4, 5, 6.2, 7, 8 |
| `SECURITY_PRIVACY_COMPLIANCE.md` | Sections 2, 3, 4, 5, 6, 8, 9 |

---

### 🎨 Indranil — Frontend Designer & Marketing Engineer

#### Core Responsibilities

| Area | Details |
|---|---|
| **Design System** | Color palette, typography, spacing tokens, Tailwind config, CSS variables, dark mode |
| **UI/UX Design** | Wireframes, page layouts, component designs, responsive breakpoints, accessibility (WCAG AA) |
| **Component Library** | Shared reusable UI components — buttons, cards, modals, tables, charts wrappers, form inputs |
| **Branding** | Logo, iconography, visual identity, brand guidelines, favicon, og:image |
| **Marketing Pages** | Landing page, pricing page, feature highlights, testimonials, CTA sections |
| **Animations & Polish** | Micro-interactions, hover effects, page transitions, loading skeletons, empty states |
| **Marketing Collateral** | Product screenshots, demo GIFs, social cards, Product Hunt assets |

#### Codebase Ownership

```
apps/
  web/
    styles/                     → Indranil (global CSS, design tokens)
    components/ui/              → Indranil (shared reusable UI components)
    app/(marketing)/            → Indranil (landing page, pricing, about)
    public/                     → Indranil (logos, icons, imagery, og images)
    tailwind.config.ts          → Indranil (design token definitions)
```

> **Collaboration note:** Indranil designs components; Aditya wires them to live data and API calls in the dashboard pages.

#### Documentation Sections Owned

| Document | Sections |
|---|---|
| `ARCHITECTURE.md` | Section 2.1 (Next.js — UI/design stack notes) |
| `PRD.md` | Section 2 Target Users (UX persona definitions) |
| `OPS_RUNBOOK.md` | Section 2.1 (Next.js env — `NEXT_PUBLIC_APP_URL`) |

---

### 🤖 Pawan — AI/ML Engineer

#### Core Responsibilities

| Area | Details |
|---|---|
| **Prompt Engine** | Template library (`prompts/templates/`), variant generation, stratified sampling, deterministic seeding with `runId` hash |
| **LLM Client** | API integration for ChatGPT (OpenAI), Gemini (Google), Perplexity — handles auth, retries, rate limiting per provider |
| **Brand Mention Extractor** | NLP pipeline (spaCy + custom rules) for detecting brand name + alias occurrences in LLM response text |
| **Sentiment Scorer** | Context-aware sentiment classification (positive / neutral / negative) with confidence score |
| **SOV Calculator** | Aggregates mention flags across prompt variants → Share-of-Voice % and Top-1 rate per provider |
| **Citation Extractor** | Extracts source URLs from Perplexity `citations` array and Gemini Grounding API source cards |
| **Gap Analyzer** | Compares brand vs. competitor mention vectors; returns ranked content gaps with recommended actions |
| **Embedding Store** | Optional pipeline — embeds LLM responses via `text-embedding-3-small`, stores refs in `embedding_refs` table for drift detection |
| **Eval Pipeline** | Maintains golden eval dataset, runs F1/accuracy scoring, blocks deploys on regression, weekly drift alerts |
| **Provider Research** | Tracks LLM provider updates, model deprecations, cost changes, new capabilities |

#### Codebase Ownership

```
services/
  python/                       → Pawan (100%)
    prompt_builder/             → Pawan
    llm_client/                 → Pawan (openai, gemini, perplexity adapters)
    extractors/                 → Pawan (brand_mention.py, citation.py)
    scorers/                    → Pawan (sentiment.py, sov.py)
    gap_analyzer/               → Pawan
    embeddings/                 → Pawan
    evals/                      → Pawan (golden_set.jsonl, run_evals.py)
    prompts/templates/          → Pawan (YAML template library)
    api/                        → Pawan (FastAPI routes for internal calls)
```

#### Documentation Sections Owned

| Document | Sections |
|---|---|
| `MODEL_PROVIDER_NOTES.md` | Entire file |
| `PROMPTING_EVALS.md` | Entire file |
| `ARCHITECTURE.md` | Section 2.3 (Python service) |
| `DATA_MODEL.md` | model_results (field definitions), citations, embedding_refs, gap_runs (result_json schema), MongoDB fragments |
| `DECISIONS.md` | ADR-005 (prompt templating) |
| `OPS_RUNBOOK.md` | Section 2.3 (Python env vars), Section 6.1 (per-run cost caps) |
| `SECURITY_PRIVACY_COMPLIANCE.md` | Section 7 (LLM Provider ToS compliance) |

---

## 3. Cross-Functional Collaboration Map

These areas require **two or more developers working together**:

| Task | Aditya | Indranil | Pawan |
|---|---|---|---|
| **New dashboard page** | Wires API calls, state management, routing | Designs layout, components, responsive behaviour | — |
| **New LLM provider** | Adds queue job, API endpoint, DB storage | Adds provider toggle/badge in UI | Implements provider client, extractor, scorer, evals |
| **Gap analysis feature** | API endpoint, result storage, run trigger | Designs gap view UI, chart layout | Gap algorithm, output format definition |
| **Run results view** | Data fetching, polling, state | Charts, layout, sentiment colour coding | Defines result payload JSON schema |
| **New prompt dimension** | — | — | Adds templates, updates eval dataset, validates F1 |
| **Auth / RBAC change** | Implements in API + middleware | Updates gated UI elements | — |
| **New metric (e.g. Top-3 rate)** | Adds to DB schema, API response, dashboard | Adds metric card/chart | Adds calculation to SOV calculator |
| **Schema migration** | Creates Prisma migration, updates API | — | Updates Python SQLAlchemy models if affected |
| **Cost optimisation** | Queue throttling, workspace spend limits | — | Token budget per provider, model selection |

---

## 4. Documentation Ownership Map — Full Reference

### 4.1 File-Level Ownership

| Document | Primary Owner | Secondary Owner | Notes |
|---|---|---|---|
| [README.md](./README.md) | Aditya | — | Project lead keeps this current |
| [PRD.md](./PRD.md) | Aditya | Pawan | Aditya owns scope; Pawan owns AI metrics |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Aditya | Pawan | Sections split by service |
| [API_CONTRACTS.md](./API_CONTRACTS.md) | Aditya | Pawan | Aditya designs endpoints; Pawan defines payload schemas for AI results |
| [DATA_MODEL.md](./DATA_MODEL.md) | Aditya | Pawan | Core tables = Aditya; AI result fields = Pawan |
| [DECISIONS.md](./DECISIONS.md) | Aditya | Pawan | ADR-005 = Pawan; rest = Aditya |
| [MODEL_PROVIDER_NOTES.md](./MODEL_PROVIDER_NOTES.md) | Pawan | — | Python service integration |
| [PROMPTING_EVALS.md](./PROMPTING_EVALS.md) | Pawan | — | Python service |
| [OPS_RUNBOOK.md](./OPS_RUNBOOK.md) | Aditya | Pawan | Python env + cost caps = Pawan |
| [SECURITY_PRIVACY_COMPLIANCE.md](./SECURITY_PRIVACY_COMPLIANCE.md) | Aditya | Pawan | ToS compliance section = Pawan |
| [CONTRIBUTORS.md](./CONTRIBUTORS.md) | Aditya | — | This file |

### 4.2 Section-Level Ownership — ARCHITECTURE.md

| Section | Owner |
|---|---|
| 2.1 Next.js Frontend | Aditya (functionality) + Indranil (design/stack) |
| 2.2 Node.js Service | Aditya |
| 2.3 Python Service | Pawan |
| 3. Data Flow | Aditya + Pawan |
| 4. Deployment Topology | Aditya |

### 4.3 Section-Level Ownership — DATA_MODEL.md

| Table / Section | Owner |
|---|---|
| workspaces, users | Aditya |
| keywords, brand_dictionaries | Aditya |
| runs, prompt_variants | Aditya (schema) + Pawan (uses) |
| model_results | Pawan (field definitions) + Aditya (Prisma write layer) |
| citations | Pawan |
| embedding_refs | Pawan |
| gap_runs | Aditya (schema) + Pawan (result_json definition) |
| MongoDB fragments | Pawan |

### 4.4 Section-Level Ownership — OPS_RUNBOOK.md

| Section | Owner |
|---|---|
| 2.1 Next.js env vars | Aditya + Indranil |
| 2.2 Node.js API env vars | Aditya |
| 2.3 Python service env vars | Pawan |
| 3. Deployment | Aditya |
| 4. Job Queue (BullMQ) | Aditya |
| 5. Monitoring & Alerting | Aditya |
| 6.1 Per-run cost cap | Pawan |
| 6.2 Workspace spend limits | Aditya |
| 7. Incident Response | Aditya |
| 8. Backup & Recovery | Aditya |

### 4.5 Section-Level Ownership — DECISIONS.md

| ADR | Owner |
|---|---|
| ADR-001 — Store Raw LLM Responses | Aditya + Pawan |
| ADR-002 — MongoDB vs. Postgres | Aditya + Pawan |
| ADR-003 — Python Pushes Results | Aditya + Pawan |
| ADR-004 — Multi-Tenancy Strategy | Aditya |
| ADR-005 — Prompt Templating | Pawan |
| ADR-006 — Auth: JWT vs. Sessions | Aditya |
| ADR-007 — Gap Analyzer Design | Aditya (endpoint) + Pawan (algorithm) |
| ADR-008 — Object Storage: R2 | Aditya |

### 4.6 Section-Level Ownership — SECURITY_PRIVACY_COMPLIANCE.md

| Section | Owner |
|---|---|
| 2. Tenant Isolation | Aditya |
| 3. Auth & RBAC | Aditya |
| 4. PII Handling | Aditya |
| 5. Data Retention | Aditya |
| 6. Secrets Management | Aditya |
| 7. Web Crawling & ToS Compliance | Pawan |
| 8. Infrastructure Security | Aditya |
| 9. Security Incident Response | Aditya |

---

## 5. Workflow Rules

1. **UI changes** — Indranil designs first; Aditya reviews for data shape requirements; Aditya implements the data/API layer
2. **API endpoint changes** — Aditya leads; Pawan must be consulted if the Python service payload or schema changes
3. **AI/scoring changes** — Pawan leads; must update `PROMPTING_EVALS.md`, run eval suite, and confirm F1 > 0.92 before merge
4. **Database schema changes** — Aditya leads; must update `DATA_MODEL.md` and create a new Prisma migration
5. **New LLM provider** — Pawan implements service-side; Aditya adds the queue job + endpoint; Indranil adds the provider badge/toggle in UI
6. **Security changes** — Aditya leads; all three reviewers must sign off before merge
7. **Architecture decisions** — Any ADR must be written to `DECISIONS.md` before implementation begins; Aditya and Pawan must agree on cross-service ADRs

---

## 6. Updating This Document

- Update this file whenever responsibilities shift, a new area of the codebase is added, or a new team member joins.
- Owner: **Aditya Singh** (project lead keeps this current).
- Review cadence: monthly, or on any major feature kick-off.

---

*Last updated: 2026-03-05*
