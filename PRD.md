# PRD — AI Visibility SaaS

**Version:** 1.0  
**Status:** MVP Active  
**Document Owner:** Aditya Singh  
**Last Updated:** 2026-02-27

> **Team:** Aditya Singh (project lead, UI/API scope) · Indranil (UX persona input) · Pawan (AI/scoring scope) — see [CONTRIBUTORS.md](./CONTRIBUTORS.md)

---

## 1. Problem Statement

> **Owner:** Aditya Singh

Traditional SEO tracks ranking on Google's blue-link results. But a rapidly growing share of search intent is now served by AI assistants — ChatGPT, Gemini, Perplexity — which synthesise answers from training data and live retrieval without showing a traditional SERP. Brands have **zero visibility** into whether they are mentioned, how positively, and how often, in those AI-generated answers.

There is no widely-available, automated tool that:
- Runs structured "buyer-intent" prompts across multiple LLM providers at scale
- Extracts brand mentions and scores them (mentioned / not mentioned / sentiment)
- Tracks Share-of-Voice (SOV) over time
- Compares a brand against named competitors
- Surfaces content-level recommendations to improve AI citation rates

---

## 2. Target Users

> **Owner:** Aditya Singh (product) · Indranil (UX persona definitions)

| User | Context |
|---|---|
| **Growth / Brand Marketer** | Manages brand across channels, reports to CMO, wants a dashboard number ("our AI SOV is 34%") |
| **SEO / GEO Specialist** | Writes and optimises content, needs keyword-level insight on what's working |
| **Product Strategist** | Tracks competitive landscape, wants share-of-voice trends vs. named rivals |
| **Agency Account Manager** | Manages multiple client workspaces, needs white-label-ready exports |

---

## 3. MVP Scope (Shipped)

> **Owner:** Aditya Singh (dashboard, API, infra items) · Pawan (AI/scoring/extraction items)

### In-Scope

- [x] **Keyword management** — CRUD keywords per workspace
- [x] **Prompt campaign runner** — generate N prompt variants per keyword, call ChatGPT / Gemini / Perplexity APIs
- [x] **Response storage** — store raw LLM responses + metadata per run
- [x] **Brand mention extraction** — Python service detects brand name + aliases in responses
- [x] **SOV scoring** — % of responses in which brand is mentioned across providers
- [x] **Top-1 detection** — is brand the *first* brand mentioned?
- [x] **Sentiment scoring** — positive / neutral / negative classification of brand mention context
- [x] **Competitor tracking** — track up to 5 competitors per keyword
- [x] **Gap analyzer** — compare brand citation vs. competitor citation, surface content gaps
- [x] **Run history** — list/view past runs with drill-down
- [x] **Next.js dashboard** — auth, workspace isolation, run triggers, results view
- [x] **REST API** — full API for programmatic access
- [x] **Multi-tenant isolation** — per-workspace data separation

### Non-Goals (V1)

- ❌ Real-time / streaming runs (async job queue is MVP, not WebSocket live)
- ❌ Custom LLM fine-tuning or prompt injection
- ❌ Google SGE / AI Overviews tracking (separate provider module, post-MVP)
- ❌ Automated content generation / publishing
- ❌ White-label theming per workspace (post-MVP)
- ❌ Mobile native apps

---

## 4. Success Metrics

> **Owner:** Aditya Singh (run latency, data freshness, cost per run) · Pawan (SOV accuracy, Top-1 rate, extraction F1)

| Metric | Definition | MVP Target |
|---|---|---|
| **Share of Voice (SOV)** | % of prompt responses in which brand is mentioned | Accurately measured ± 3% |
| **Top-1 Rate** | % of responses where brand is first brand mentioned | Accurately measured ± 3% |
| **Cost per Run** | Total API cost (LLM tokens) per keyword run | < $0.10 per keyword (N=10 variants, 3 providers) |
| **Run Latency P95** | Time from trigger to results available in UI | < 90 seconds |
| **Data Freshness** | Max age of most recent run available to user | On-demand + scheduled daily |
| **Extraction Accuracy** | Brand mention detection F1 score on eval set | > 0.92 |

---

## 5. Milestones

> **Owner:** Aditya Singh (project lead — milestone tracking)

| Milestone | Target | Status |
|---|---|---|
| M0 — Architecture & contracts finalised | Week 1 | ✅ Done |
| M1 — Python LLM service + scoring live | Week 2 | ✅ Done |
| M2 — Node.js API + job queue working | Week 2 | ✅ Done |
| M3 — Next.js UI — run + results views | Week 3 | 🔄 In Progress |
| M4 — Gap analyzer live | Week 4 | ⬜ Upcoming |
| M5 — Multi-tenant + billing stubs | Week 5 | ⬜ Upcoming |
| M6 — Beta with 3 external customers | Week 6 | ⬜ Upcoming |
