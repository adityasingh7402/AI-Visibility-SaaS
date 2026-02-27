# OPS RUNBOOK — AI Visibility SaaS

**Last Updated:** 2026-02-27  
**Owner:** Aditya Singh  
**Audience:** Engineers deploying or operating the platform

---

## 1. Architecture at a Glance (Ops View)

| Service | Platform | URL Pattern |
|---|---|---|
| Next.js UI (`apps/web`) | Vercel | `https://app.aivisibility.app` |
| Node.js API (`apps/api`) | Railway / Render | `https://api.aivisibility.app` |
| Python Service (`services/python`) | Railway / Render | `https://ai-svc.internal` (private) |
| PostgreSQL | Supabase | Private connection string |
| Redis | Upstash | Private connection string |
| Object Storage | Cloudflare R2 | `https://r2.aivisibility.app` (private) |

---

## 2. Environment Variables

### 2.1 Next.js (`apps/web/.env.local`)

```env
NEXT_PUBLIC_API_URL=https://api.aivisibility.app/v1
NEXT_PUBLIC_APP_URL=https://app.aivisibility.app
```

### 2.2 Node.js API (`apps/api/.env`)

```env
# App
NODE_ENV=production
PORT=3001
API_BASE_URL=https://api.aivisibility.app

# Database
DATABASE_URL=postgresql://user:pass@host:5432/aivisibility?sslmode=require
DIRECT_URL=postgresql://user:pass@host:5432/aivisibility  # for migrations

# Auth
JWT_SECRET_PRIVATE_KEY=<RS256 private key (base64)>
JWT_SECRET_PUBLIC_KEY=<RS256 public key (base64)>
JWT_ACCESS_EXPIRY=3600        # seconds
JWT_REFRESH_EXPIRY=2592000    # 30 days in seconds

# Redis (BullMQ)
REDIS_URL=rediss://user:pass@upstash-host:6380

# Python Service
PYTHON_SERVICE_URL=https://ai-svc.internal
PYTHON_SERVICE_SECRET=<shared hmac secret>

# Object Storage (Cloudflare R2)
R2_ACCOUNT_ID=<cf account id>
R2_ACCESS_KEY_ID=<r2 key>
R2_SECRET_ACCESS_KEY=<r2 secret>
R2_BUCKET_NAME=ai-visibility-responses
R2_PUBLIC_URL=https://r2.aivisibility.app

# Monitoring
SENTRY_DSN=<sentry dsn>
```

### 2.3 Python Service (`services/python/.env`)

```env
# App
ENVIRONMENT=production
PORT=8000
INTERNAL_SECRET=<shared hmac secret — must match Node API>

# LLM Providers
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...
GOOGLE_API_KEY=...
PERPLEXITY_API_KEY=pplx-...

# Database (direct write for results)
DATABASE_URL=postgresql://user:pass@host:5432/aivisibility?sslmode=require

# Monitoring
SENTRY_DSN=<sentry dsn>
```

---

## 3. Deployment

### 3.1 Initial Setup

```bash
# 1. Clone repo
git clone https://github.com/adityasingh7402/AI-Visibility-SaaS.git
cd AI-Visibility-SaaS

# 2. Copy env files
cp apps/web/.env.example apps/web/.env.local
cp apps/api/.env.example apps/api/.env
cp services/python/.env.example services/python/.env
# Fill in secrets

# 3. Run DB migrations
cd apps/api
npx prisma migrate deploy

# 4. Start all services (local)
docker-compose up
```

### 3.2 Production Deploy

**Next.js (Vercel):**
- Connected to `main` branch — auto-deploys on push
- Preview deployments on every PR

**Node.js API (Railway):**
```bash
# Railway auto-deploys from main branch
# Manual deploy:
railway up --service api
```

**Python Service (Railway):**
```bash
railway up --service python-svc
```

**DB Migrations (run before API deploy):**
```bash
cd apps/api
DATABASE_URL=<prod url> npx prisma migrate deploy
```

---

## 4. Job Queue (BullMQ)

### 4.1 Queues

| Queue | Workers | Max Concurrency | Retry |
|---|---|---|---|
| `visibility-runs` | Node API workers | 5 | 3x exponential |
| `gap-analysis` | Node API workers | 3 | 2x exponential |

### 4.2 Worker Settings

```typescript
// apps/api/src/queues/visibilityWorker.ts
const worker = new Worker('visibility-runs', processRun, {
  connection: redis,
  concurrency: 5,
  limiter: { max: 10, duration: 1000 }, // 10 jobs/sec max
});
```

### 4.3 Monitoring Queue Health

```bash
# BullMQ Dashboard (Bull Board)
# Available at: https://api.aivisibility.app/admin/queues
# Protected by admin role JWT

# CLI check:
redis-cli -u $REDIS_URL llen "bull:visibility-runs:wait"
```

---

## 5. Monitoring & Alerting

### 5.1 Stack

| Tool | Purpose |
|---|---|
| **Sentry** | Error tracking (Node + Python + Next.js) |
| **Uptime Robot / Better Uptime** | Endpoint uptime (99.9% SLA target) |
| **Railway Metrics** | CPU, memory, latency per service |
| **Postgres Dashboard (Supabase)** | Query performance, connection count |
| **Slack #alerts** | All alert destinations route here |

### 5.2 Key Alerts

| Alert | Condition | Severity |
|---|---|---|
| API Error Rate High | 5xx rate > 1% over 5 min | 🔴 Critical |
| Run Queue Depth | `visibility-runs:wait` > 50 | 🟡 Warning |
| Python Service Down | Health check fails 2x | 🔴 Critical |
| DB Connection Exhausted | Open connections > 80% of pool | 🔴 Critical |
| LLM Provider Error Rate | Any provider 5xx > 20% over 10 min | 🟡 Warning |
| Cost Spike | LLM spend > $20/hour | 🟡 Warning |
| SOV Drift | >15% weekly drop for any customer keyword | 🔵 Info |

---

## 6. Cost Controls

### 6.1 Per-Run Cost Cap

Each run has a maximum token budget enforced by the Python service:

```python
MAX_TOKENS_PER_RUN = {
    "chatgpt": 50_000,    # ~$0.25 at gpt-4o price
    "gemini": 100_000,    # ~$0.35 at pro price
    "perplexity": 30_000, # ~$0.03
}
```

Runs exceeding the cap are aborted with status `COST_LIMIT_EXCEEDED`.

### 6.2 Workspace Monthly Spend Limit

- Free tier: $2/month LLM budget
- Pro tier: $50/month
- Enterprise: configurable
- On limit hit: runs return `402 Payment Required`; email sent to workspace owner

### 6.3 LLM Provider Budget Alerts

Set hard limits in each provider's billing dashboard:
- OpenAI: $100/month hard limit, alert at $80
- Google AI: $100/month, alert at $80
- Perplexity: $50/month, alert at $40

---

## 7. Incident Response

### Severity Levels

| P0 | Total outage — all customers affected |
| P1 | Partial outage — major feature broken for all/many |
| P2 | Degraded performance or single-customer issue |
| P3 | Minor bug; workaround exists |

### P0/P1 Response Steps

1. **Page on-call** via Slack #alerts or PagerDuty
2. **Acknowledge** within 5 min (P0) / 15 min (P1)
3. **Assess** — check Sentry, Railway metrics, Supabase
4. **Communicate** — post status update to status page (statuspage.io) + Slack #incidents
5. **Mitigate** — rollback, restart service, or apply hot patch
6. **Resolve** — confirm service restored, close incident
7. **Post-mortem** — within 48 hours; update this runbook if process gaps found

### Common Fixes

```bash
# Restart Node API
railway restart --service api

# Restart Python service
railway restart --service python-svc

# Drain and restart queue workers
# (via Bull Board UI or):
redis-cli -u $REDIS_URL del "bull:visibility-runs:active"

# Roll back migration (emergency only)
cd apps/api
DATABASE_URL=<prod> npx prisma migrate resolve --rolled-back <migration_name>

# Force-complete a stuck run
psql $DATABASE_URL -c "UPDATE runs SET status='FAILED', error_message='Manual override' WHERE id='run_01HZ...';"
```

---

## 8. Backup & Recovery

| Resource | Backup | RTO | RPO |
|---|---|---|---|
| PostgreSQL | Supabase daily snapshots (7-day retention) | 4 hours | 24 hours |
| R2 Object Storage | Versioning enabled; cross-region replication | 2 hours | 1 hour |
| Redis | Upstash persistence (AOF) | 30 min | ~5 min |

To restore Postgres from backup: use Supabase Dashboard → Backups → Restore.
