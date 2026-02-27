# SECURITY, PRIVACY & COMPLIANCE — AI Visibility SaaS

**Last Updated:** 2026-02-27  
**Owner:** Aditya Singh  
**Review Cadence:** Quarterly

---

## 1. Data Classification

| Class | Examples | Access |
|---|---|---|
| **Public** | Product docs, public API contracts | Anyone |
| **Internal** | Source code, architecture docs | Team only |
| **Confidential** | Customer keyword lists, run results, brand dictionaries | Per-workspace with auth |
| **Restricted** | API keys, secrets, user credentials | Secrets manager only, never logged |

---

## 2. Tenant Isolation

All customer data is isolated at the **workspace level**.

### 2.1 Database Isolation

- Every Postgres table that holds customer data has a `workspace_id` column.
- **All queries** — including via ORM and raw SQL — are filtered by `workspace_id` extracted from the validated JWT.
- Prisma middleware enforces `workspace_id` injection automatically:

```typescript
// middleware/tenantScope.ts
prisma.$use(async (params, next) => {
  const workspaceId = getWorkspaceIdFromContext();
  if (params.model && TENANT_MODELS.includes(params.model)) {
    params.args.where = { ...params.args.where, workspaceId };
  }
  return next(params);
});
```

- Workspace ID is **never** taken from the request body — only from the validated JWT claim.

### 2.2 File Storage Isolation

- S3/R2 raw response blobs are stored under `/{workspace_id}/{run_id}/...`.
- Pre-signed URLs scoped to the workspace prefix only.
- No cross-workspace URL access permitted.

### 2.3 API Isolation

- Workspace-scoped resources (runs, keywords, etc.) return `404 NOT_FOUND` — **not** `403 FORBIDDEN` — when accessed by a token from a different workspace, to avoid enumeration.

---

## 3. Authentication & Authorization

### 3.1 JWT Tokens

- Signed with RS256 (asymmetric key pair)
- Claims: `sub` (user_id), `workspace_id`, `role`, `exp` (1h access token), `iat`
- Refresh tokens: 30-day sliding expiry, stored as httpOnly cookie (encrypted)
- Token rotation on refresh; previous refresh token invalidated immediately (single-use)

### 3.2 Role-Based Access Control (RBAC)

| Role | Can Read | Can Write | Can Admin |
|---|---|---|---|
| `viewer` | ✅ | ❌ | ❌ |
| `editor` | ✅ | ✅ | ❌ |
| `admin` | ✅ | ✅ | ✅ (workspace) |
| `owner` | ✅ | ✅ | ✅ (billing too) |

### 3.3 API Key Access (Post-MVP)

- Long-lived API keys for programmatic access; stored as hashed (bcrypt) values.
- Keys scoped to workspace with configurable role cap.
- Rate-limited per key.

---

## 4. PII Handling

### 4.1 What is PII in this system?

| Field | PII Risk | Handling |
|---|---|---|
| User email | Medium | Encrypted at rest (AES-256 via Supabase) |
| User name | Low | Encrypted at rest |
| LLM prompt text | Low-Medium | May contain brand/competitor info; treated as confidential |
| LLM response text | Low | Treated as confidential (workspace data) |
| IP address | Medium | Logged for fraud detection only; not attached to run results |

### 4.2 Logging Redaction

- User emails and workspace names are **never** logged in plain text in application logs.
- JWT tokens are redacted in log lines (replaced with `[JWT_REDACTED]`).
- API keys redacted as `[APIKEY_REDACTED]`.
- Logs are structured JSON (no free-text interpolation that could accidentally include secrets).

---

## 5. Data Retention

| Data | Retention | Deletion Method |
|---|---|---|
| User accounts | Until account deletion request + 30 days | Soft delete → hard delete at 30d |
| Workspace run results (Postgres) | 2 years | Automated TTL job |
| Raw response blobs (S3/R2) | 90 days active, then archive tier | Lifecycle policy |
| Raw fragments (MongoDB) | 90 days | TTL index on `created_at` |
| Audit logs | 3 years | Cold storage after 1 year |
| Billing records | 7 years (legal) | Immutable cold storage |

### 5.1 Account Deletion (Right to Erasure)

- On workspace deletion: all runs, keywords, model results, and user records are hard-deleted within 7 days.
- S3/R2 blobs deleted within 24 hours via deletion job.
- Email deletion confirmation sent to workspace owner.

---

## 6. Secrets Management

- All secrets (API keys, DB URLs, signing keys) stored in environment variables.
- **Never** commit secrets to Git — `.env` is in `.gitignore`; CI uses vault/secrets manager.
- Recommended: **Doppler** or **AWS Secrets Manager** for production.
- Rotate all LLM provider API keys quarterly or on suspected exposure.
- Principle of least privilege: each service only receives the secrets it needs.

---

## 7. Web Crawling, Robots.txt & ToS

The platform does **not** crawl or scrape websites as part of its core function — it calls official LLM provider APIs only. However, for citation analysis (URLs returned by Perplexity):

- We store the **URL and title** returned by the provider — we do **not** fetch or scrape the linked page.
- Downstream content analysis from cited URLs would require: robots.txt compliance, rate limiting, and ToS review per target domain.
- **Current MVP stance:** citation URLs stored as-is; no crawling.

### LLM Provider ToS Compliance

| Provider | Key Restriction | Our Status |
|---|---|---|
| OpenAI | No training data extraction | ✅ Compliant — we score responses, don't extract training data |
| Google | No prompt injection to circumvent filters | ✅ Compliant |
| Perplexity | API use only (no scraping their web UI) | ✅ Compliant |

---

## 8. Infrastructure Security

- All inter-service communication over HTTPS (TLS 1.3).
- Internal services (Node → Python) on private network — not exposed to public internet.
- Postgres: SSL required, connection pooling (PgBouncer/Supabase pooler), never publicly accessible.
- Redis: password-authenticated, private network only.
- S3/R2: private bucket; no public access; pre-signed URLs for temporary access (15-min expiry).
- Dependency scanning: automated via `npm audit` + `pip-audit` in CI.
- SAST: CodeQL on PRs to main.

---

## 9. Incident Response (Security)

1. **Detect** — monitoring alert OR user report
2. **Contain** — rotate compromised credentials immediately; if DB breach suspected, revoke all tokens
3. **Assess** — determine scope (which workspaces, what data)
4. **Notify** — affected customers within 72 hours (GDPR requirement)
5. **Remediate** — patch vulnerability, re-audit affected area
6. **Post-mortem** — blameless review; update runbook

Contact: security@aivisibility.app
