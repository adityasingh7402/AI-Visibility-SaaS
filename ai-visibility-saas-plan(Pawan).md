# My Plan — GEO Platform Python Service

**Author:** Pawan Kumar Yadav — AI/ML Engineer
**Date:** March 2026

---

## What I'm Building

I'm building the **AI engine** behind our GEO (Generative Engine Optimization) platform. It's a Python service that takes a product page URL and does something no other tool does — it tells businesses exactly **how visible their product is to AI assistants** like ChatGPT, Gemini, and Grok, and gives them specific, ready-to-use content to fix it.

This service is the core intelligence layer. The frontend team handles the dashboard, auth, and payments. My service powers everything behind the "Analyze" button.

---

## How It Works

I'm building **5 AI agents** that work together in a pipeline:

| Agent | What It Does | Time |
|---|---|---|
| **Agent 1 — Crawler** | Fetches the page, extracts content, images, meta tags, schema markup | ~3s |
| **Agent 2 — Researcher** | Searches the internet for competitors, keyword gaps, web presence (Wikipedia, G2, Forbes) | ~20s |
| **Agent 3 — LLM Tester** | Asks ChatGPT, Gemini, and Grok about the product category, checks if they mention the brand | ~25s |
| **Agent 4 — Image Analyzer** | Uses vision AI to analyze product images, scores alt text quality | ~10s |
| **Agent 5 — Optimizer** | Synthesizes everything, generates GEO Score, recommendations, and ready-to-use content | ~15s |

Agents 2, 3, and 4 run **in parallel** after Agent 1 finishes. Agent 5 runs last. Total: **~30-50 seconds per URL.**

I'm using **LangGraph** to orchestrate this pipeline — it handles the parallel execution, shared state, and error recovery.

---

## My LLM Strategy

I'm not using one expensive model for everything. I designed a **3-tier routing strategy**:

| Tier | Models | Used For | Cost |
|---|---|---|---|
| **Tier 1** — Groq | Llama 3.3 70B, Llama 3.1 8B | Internal reasoning, content generation (90% of calls) | ~$0.05/run |
| **Tier 2** — Gemini Free | Gemini 2.0 Flash Vision | Image analysis | $0 |
| **Tier 3** — Commercial | GPT-4o, Gemini, Grok | Visibility testing only (must test real providers) | ~$0.06/run |

**Total cost per analysis: ~$0.11** — about 70% cheaper than using GPT-4o for everything.

---

## What Makes This Special (4 Innovations)

Beyond the core analysis, I'm adding features that go beyond what was originally scoped:

**1. AI Content Generator** — I don't just say "add a FAQ section." I generate the FAQ, the meta tags, the rewritten product description — all copy-paste ready. Powered by Llama 70B on Groq.

**2. Competitor Battle Cards** — Auto-generated competitive analysis for every competitor. Shows how AI positions them vs the user, what keywords they dominate, and a suggested comparison page draft.

**3. AI-Ready Content Tips** — Industry-specific tips on how to write content that LLMs prefer to cite. Q&A format, specific data points, definitive statements.

**4. GEO Score™** — A 0-100 score with 7 sub-scores (Web Presence, Authority, LLM Mentions, Page Quality, Technical SEO, Image SEO, Competitor Gap). Every recommendation comes with confidence labels (🟢 HIGH / 🟡 MEDIUM / 🔴 LOW) and evidence.

---

## My Testing Plan

I'm building a **full test pyramid**:

- **7 Unit Test files** — one per agent/module, mocked dependencies, runs on every commit
- **3 Integration Tests** — full pipeline flow, API contract validation, graceful degradation
- **3 E2E Tests** — real API calls on staging (Groq + Gemini free tier)
- **Eval Pipeline** — 50-example golden dataset, brand mention F1 > 0.92 required, blocks deployment on regression
- **8 Edge Cases** — 404 pages, SPAs, no images, non-English, huge pages, etc.
- **Performance Targets** — full pipeline < 60s, memory < 512MB

---

## Tech Stack

| | Technology |
|---|---|
| Language | Python 3.12+ |
| API | FastAPI |
| Orchestration | LangGraph |
| LLM Interface | LiteLLM (Groq, OpenAI, Gemini, xAI) |
| Search | Tavily + Google Custom Search |
| NLP | spaCy + HuggingFace (local sentiment) |
| Data | Pydantic v2 + Polars |
| Deploy | Docker |
| Package Manager | uv |
| Testing | pytest + mypy |

---

## Deliverables

I'm delivering a **Dockerized Python service** with:
- `POST /internal/analyze` — full URL analysis (5 agents, parallel pipeline)
- `POST /internal/analyze-keyword` — keyword-only mode (Agent 3 solo)
- `GET /health` — readiness check
- **35+ source files**, fully typed, structured JSON logging
- Full test suite + eval pipeline
- Docker image ready to deploy alongside the Node.js backend

---

## Timeline

| Phase | What | Weeks |
|---|---|---|
| 1 | Project setup, config, schemas | 1 |
| 2 | Agent 1: Page Crawler | 1 |
| 3 | Agent 2: Researcher + Web Presence | 2 |
| 4 | Agent 3: LLM Visibility Tester | 1-2 |
| 5 | Agent 4: Image Analyzer | 1 |
| 6 | Agent 5: Optimizer + Innovations | 2 |
| 7-8 | Orchestrator + API + Testing + QA | 2 |
| | **Total** | **~10-11 weeks** |

---

## What I Need From the Team

| From | What I Need |
|---|---|
| **Frontend** | Dashboard UI to display my JSON response (GEO Score, recommendations, battle cards, generated content sections) |
| **Backend** | Node.js endpoint that calls my `POST /internal/analyze` and stores the response |
| **DevOps** | Deploy my Docker container alongside the Node.js service |
| **API Keys** | Groq, Google (Gemini + CSE), Tavily, OpenAI, xAI (Grok) |
