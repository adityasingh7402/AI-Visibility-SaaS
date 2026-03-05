# DECISIONS — AI Visibility SaaS (ADR-Lite)

A running log of architectural and product decisions with date, context, and rationale. New decisions are appended at the bottom.

> **Document Owner:** Aditya Singh · **AI/scoring ADRs:** Pawan — see [CONTRIBUTORS.md](./CONTRIBUTORS.md)

---

## Decision Log

---

### ADR-001 · Store Raw LLM Responses?

**Date:** 2026-02-20  
**Status:** ✅ Accepted  
**Owner:** Aditya Singh + Pawan

**Context:**  
LLM responses are the source of truth for scoring. If we only store scores, we lose the ability to:
- Re-score if the scoring algorithm changes
- Debug false positives/negatives
- Audit results for customers

**Decision:**  
Store raw responses. Response text stored in Postgres `model_results.response_text` for responses < 8KB. For larger responses (rare), store in R2 and reference via `response_blob_url`.

**Rationale:**  
Re-scoring without raw data is impossible. Storage cost is negligible (~$0.015/GB on R2). 90-day retention balances auditability with cost.

**Consequences:**  
- 90-day retention policy required to manage storage costs
- Need cleanup job that moves to archive/deletes after 90 days
- Potential PII risk if prompts/responses contain customer-inputted identifiable info → mitigated by workspace isolation

---

### ADR-002 · MongoDB vs. Postgres+Vector for Fragments

**Date:** 2026-02-20  
**Status:** ✅ Accepted (Postgres Primary, MongoDB Optional)  
**Owner:** Aditya Singh + Pawan

**Context:**  
Raw LLM responses are semi-structured. We evaluated:
- **Option A:** Postgres JSONB columns
- **Option B:** MongoDB for raw fragment storage
- **Option C:** Postgres primary + MongoDB optional for raw blobs

**Decision:**  
Use Postgres as the primary store (JSONB for scores, TEXT for response body). MongoDB is optional and only activated if raw fragment search becomes a requirement. R2 object storage for large raw JSON blobs.

**Rationale:**  
- Avoiding two databases in MVP reduces operational complexity
- Postgres JSONB is sufficient for structured scoring data
- MongoDB adds value only for full-text search over response fragments — not a V1 requirement
- Can migrate if needed; decision is reversible

**Consequences:**  
- DATA_MODEL.md references MongoDB as optional
- If full-text fragment search is added in V2, revisit this decision

---

### ADR-003 · Python Pushes Results vs. Node Pulls

**Date:** 2026-02-21  
**Status:** ✅ Accepted (Python Pushes)  
**Owner:** Aditya Singh (Node callback) + Pawan (Python push logic)

**Context:**  
Two patterns considered for delivering LLM run results from Python service to Node:
- **Pull:** Node polls Python on a timer until results are ready
- **Push:** Python calls a Node callback URL when processing is complete

**Decision:**  
Python **pushes** results via HTTP POST to Node's internal callback endpoint when the run is complete.

**Rationale:**  
- Eliminates polling overhead and latency
- Python controls when it's done — it knows best
- Node callback is simple (receive → write to DB → update run status)
- Simpler than an event bus for MVP scale

**Consequences:**  
- Node must expose a secure internal callback endpoint (`POST /internal/runs/:id/complete`)
- Callback uses shared HMAC secret for auth (not JWT)
- If Python crashes mid-run, Node must have a timeout fallback to mark run as FAILED (10-minute job timeout)

---

### ADR-004 · Multi-Tenancy Strategy: Row-Level Isolation

**Date:** 2026-02-21  
**Status:** ✅ Accepted  
**Owner:** Aditya Singh

**Context:**  
Options for multi-tenant data isolation:
- **Option A:** Separate database per tenant (strong isolation, expensive)
- **Option B:** Separate schema per tenant (moderate isolation, moderate complexity)
- **Option C:** Shared schema with `workspace_id` on all tables (simplest, adequate isolation via application layer)

**Decision:**  
Row-level isolation (Option C) with `workspace_id` enforced by Prisma middleware.

**Rationale:**  
- MVP scale doesn't justify per-tenant databases
- Application-layer enforcement is sufficient given the threat model (the main risk is bugs, not adversarial tenants)
- Easier to operate and migrate
- Supabase RLS (Row Level Security) can be added as an additional layer if compliance requires it (post-MVP)

**Consequences:**  
- Every Postgres query touching tenant data MUST include `workspace_id` filter
- Prisma middleware automates this — code review must verify middleware is never bypassed
- If enterprise compliance (SOC2, HIPAA) requires stronger isolation: revisit with schema-per-tenant

---

### ADR-005 · Prompt Templating: Static Library vs. LLM-Generated Variants

**Date:** 2026-02-22  
**Status:** ✅ Accepted (Static Library + Stratified Sampling)  
**Owner:** Pawan

**Context:**  
Two approaches to generating prompt variants:
- **Option A:** Static template library, stratified sampling
- **Option B:** Use an LLM to generate N diverse prompts from a seed keyword (meta-prompting)

**Decision:**  
Static template library with stratified sampling for MVP.

**Rationale:**  
- Option B adds latency (extra LLM call) and cost before the run even starts
- Static templates are reproducible, debuggable, and auditable
- Meta-prompting variance makes eval harder — hard to know if SOV change is real or prompt-distribution artifact
- Can add LLM-generated variants as an opt-in "deep mode" post-MVP

**Consequences:**  
- Template library must be maintained and expanded over time
- Need a content process for adding new template dimensions (personas, verticals, etc.)
- If template library becomes a competitive differentiator, invest in quality over quantity

---

### ADR-006 · Auth: JWT vs. Session Tokens

**Date:** 2026-02-22  
**Status:** ✅ Accepted (JWT with Refresh Rotation)  
**Owner:** Aditya Singh

**Context:**  
Options for user authentication:
- **Option A:** Server-side sessions (session ID in cookie, server state in Redis)
- **Option B:** Stateless JWT (signed tokens, no server state)
- **Option C:** JWT + refresh token rotation (access token short-lived, refresh in httpOnly cookie)

**Decision:**  
Option C: JWT with refresh token rotation.

**Rationale:**  
- Stateless API is easier to scale horizontally (no sticky sessions)
- Short-lived access tokens (1h) limit blast radius of token theft
- Refresh token rotation invalidates stolen refresh tokens quickly
- httpOnly cookie for refresh token prevents XSS access

**Consequences:**  
- Must implement token rotation logic (invalidate old refresh token on use)
- Must handle concurrent requests that both try to refresh simultaneously (use Redis lock)
- If a refresh token is stolen and rotated by attacker, legitimate user gets logged out — acceptable trade-off

---

### ADR-007 · Gap Analyzer: In-Process vs. Separate Endpoint

**Date:** 2026-02-23  
**Status:** ✅ Accepted (Separate Async Endpoint)  
**Owner:** Aditya Singh (API endpoint design) + Pawan (gap algorithm)

**Context:**  
Gap analysis could be:
- **Option A:** Run synchronously as part of each visibility run (automatic)
- **Option B:** Separate on-demand endpoint, async job

**Decision:**  
Separate on-demand async endpoint (`POST /gap/run`).

**Rationale:**  
- Not every customer wants gap analysis on every run — it adds cost and latency
- Separation allows gap analysis to aggregate across multiple runs and providers (richer insight)
- Async pattern consistent with visibility runs
- Customers who need it can trigger it explicitly or set up scheduled gap analysis

**Consequences:**  
- UI needs separate "Run Gap Analysis" button / scheduled setting
- Gap analysis results stored separately in `gap_runs` table

---

### ADR-008 · Object Storage: S3 vs. Cloudflare R2

**Date:** 2026-02-24  
**Status:** ✅ Accepted (Cloudflare R2)  
**Owner:** Aditya Singh

**Context:**  
Need object storage for raw LLM response blobs.

**Decision:**  
Cloudflare R2.

**Rationale:**  
- **Zero egress fees** — critical given that we'll be reading blobs frequently for re-scoring
- S3-compatible API means switching cost is low if needed
- Cheaper storage at scale
- Integrated with Cloudflare CDN if we ever need public delivery

**Consequences:**  
- Use AWS SDK v3 with R2 endpoint configured (drop-in compatible)
- Pre-signed URL generation works identically to S3
