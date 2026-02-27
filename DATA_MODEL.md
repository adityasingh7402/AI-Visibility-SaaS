# DATA MODEL — AI Visibility SaaS

**Primary DB:** PostgreSQL (via Supabase)  
**Optional:** MongoDB (raw LLM response fragments)  
**ORM:** Prisma (Node.js service)  
**Last Updated:** 2026-02-27

---

## 1. Entity Overview

```
Workspace
  └── Keyword (many)
        └── BrandDictionary (1, shared or per-keyword)
        └── Run (many)
              └── PromptVariant (many)
                    └── ModelResult (many, one per provider)
                          └── Citation (many)
                          └── EmbeddingRef (1, optional)
  └── Fragment (MongoDB, optional — raw response text)
```

---

## 2. PostgreSQL Schema

### `workspaces`

```sql
CREATE TABLE workspaces (
  id            TEXT PRIMARY KEY,              -- ulid: ws_01HZ...
  name          TEXT NOT NULL,
  slug          TEXT NOT NULL UNIQUE,
  plan          TEXT NOT NULL DEFAULT 'free', -- free | pro | enterprise
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### `users`

```sql
CREATE TABLE users (
  id            TEXT PRIMARY KEY,             -- ulid
  workspace_id  TEXT NOT NULL REFERENCES workspaces(id),
  email         TEXT NOT NULL UNIQUE,
  name          TEXT,
  role          TEXT NOT NULL DEFAULT 'viewer', -- owner | admin | editor | viewer
  password_hash TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### `keywords`

```sql
CREATE TABLE keywords (
  id                   TEXT PRIMARY KEY,       -- ulid: kw_01HZ...
  workspace_id         TEXT NOT NULL REFERENCES workspaces(id),
  text                 TEXT NOT NULL,          -- e.g. "best CRM for startups"
  category             TEXT,                   -- e.g. "CRM", "Fintech"
  competitors          TEXT[],                 -- brand name strings
  brand_dictionary_id  TEXT REFERENCES brand_dictionaries(id),
  is_active            BOOLEAN NOT NULL DEFAULT TRUE,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(workspace_id, text)
);
```

---

### `brand_dictionaries`

Defines the brand name and its aliases used for mention detection.

```sql
CREATE TABLE brand_dictionaries (
  id            TEXT PRIMARY KEY,             -- ulid: bd_01HZ...
  workspace_id  TEXT NOT NULL REFERENCES workspaces(id),
  brand_name    TEXT NOT NULL,               -- canonical brand name
  aliases       TEXT[],                      -- e.g. ["Co.", "Our Brand", "OurBrand"]
  is_default    BOOLEAN NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### `runs`

One run = one keyword × one trigger event.

```sql
CREATE TABLE runs (
  id                    TEXT PRIMARY KEY,       -- ulid: run_01HZ...
  workspace_id          TEXT NOT NULL REFERENCES workspaces(id),
  keyword_id            TEXT NOT NULL REFERENCES keywords(id),
  brand_dictionary_id   TEXT REFERENCES brand_dictionaries(id),
  status                TEXT NOT NULL DEFAULT 'QUEUED',
                        -- QUEUED | RUNNING | COMPLETED | FAILED | CANCELLED
  providers             TEXT[],                -- ["chatgpt","gemini","perplexity"]
  prompt_variant_count  INTEGER NOT NULL DEFAULT 10,
  triggered_by          TEXT,                  -- user_id or 'scheduler'
  webhook_url           TEXT,
  idempotency_key       TEXT UNIQUE,
  error_message         TEXT,
  started_at            TIMESTAMPTZ,
  completed_at          TIMESTAMPTZ,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_runs_workspace_keyword ON runs(workspace_id, keyword_id);
CREATE INDEX idx_runs_status ON runs(status);
```

---

### `prompt_variants`

Each generated prompt for a run.

```sql
CREATE TABLE prompt_variants (
  id            TEXT PRIMARY KEY,             -- ulid: pv_01HZ...
  run_id        TEXT NOT NULL REFERENCES runs(id),
  template_id   TEXT,                        -- which template was used
  prompt_text   TEXT NOT NULL,               -- final rendered prompt
  variant_index INTEGER NOT NULL,            -- 0-based index
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_pv_run ON prompt_variants(run_id);
```

---

### `model_results`

One result per (prompt_variant × provider).

```sql
CREATE TABLE model_results (
  id                TEXT PRIMARY KEY,         -- ulid: mr_01HZ...
  run_id            TEXT NOT NULL REFERENCES runs(id),
  prompt_variant_id TEXT NOT NULL REFERENCES prompt_variants(id),
  provider          TEXT NOT NULL,           -- chatgpt | gemini | perplexity
  model_version     TEXT,                    -- e.g. "gpt-4o", "gemini-1.5-pro"
  response_text     TEXT,                    -- full response (or null if stored in blob)
  response_blob_url TEXT,                    -- S3/R2 URL to full raw JSON
  brand_mentioned   BOOLEAN NOT NULL DEFAULT FALSE,
  mention_rank      INTEGER,                 -- position of brand in brand mention order (1-based)
  is_top1           BOOLEAN NOT NULL DEFAULT FALSE,
  sentiment         TEXT,                    -- positive | neutral | negative
  confidence_score  NUMERIC(5,4),           -- 0.0000 – 1.0000
  prompt_tokens     INTEGER,
  completion_tokens INTEGER,
  latency_ms        INTEGER,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mr_run ON model_results(run_id);
CREATE INDEX idx_mr_provider ON model_results(provider);
```

---

### `citations`

Source URLs returned by providers (primarily Perplexity).

```sql
CREATE TABLE citations (
  id               TEXT PRIMARY KEY,          -- ulid: cit_01HZ...
  model_result_id  TEXT NOT NULL REFERENCES model_results(id),
  url              TEXT NOT NULL,
  domain           TEXT,
  title            TEXT,
  position         INTEGER,                  -- order in citation list
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_citations_model_result ON citations(model_result_id);
```

---

### `embedding_refs`

Optional: references to vector embeddings for drift/similarity checks.

```sql
CREATE TABLE embedding_refs (
  id               TEXT PRIMARY KEY,
  model_result_id  TEXT NOT NULL REFERENCES model_results(id) UNIQUE,
  vector_id        TEXT NOT NULL,            -- ID in vector store (pgvector or Pinecone)
  model            TEXT NOT NULL,           -- e.g. "text-embedding-3-small"
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

### `gap_runs`

Records of gap analysis jobs.

```sql
CREATE TABLE gap_runs (
  id            TEXT PRIMARY KEY,
  workspace_id  TEXT NOT NULL REFERENCES workspaces(id),
  keyword_id    TEXT NOT NULL REFERENCES keywords(id),
  run_id        TEXT REFERENCES runs(id),
  competitors   TEXT[],
  depth         TEXT NOT NULL DEFAULT 'standard',
  status        TEXT NOT NULL DEFAULT 'QUEUED',
  result_json   JSONB,                       -- full gap result stored inline
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at  TIMESTAMPTZ
);
```

---

## 3. MongoDB Schema (Optional — Raw Fragments)

Used if raw LLM response JSON is too large or noisy for Postgres.

**Collection: `fragments`**

```json
{
  "_id": "ObjectId",
  "model_result_id": "mr_01HZ...",
  "run_id": "run_01HZ...",
  "workspace_id": "ws_01HZ...",
  "provider": "chatgpt",
  "raw_response": { ... },           // full provider API response object
  "extracted_text": "...",           // cleaned response text
  "mentions": [
    {
      "brand": "Acme Corp",
      "start": 142,
      "end": 151,
      "context": "...Acme Corp is known for...",
      "sentiment": "positive"
    }
  ],
  "created_at": "2026-02-27T15:30:00Z"
}
```

**Indexes:**
- `{ model_result_id: 1 }` (unique)
- `{ run_id: 1 }`
- `{ workspace_id: 1, created_at: -1 }`

---

## 4. Data Retention

| Data Type | Retention |
|---|---|
| Run metadata (Postgres) | 2 years |
| Raw response blobs (S3/R2) | 90 days, then archive |
| Raw fragments (MongoDB) | 90 days |
| Embedding vectors | 1 year |
| Audit logs | 3 years |

See [SECURITY_PRIVACY_COMPLIANCE.md](./SECURITY_PRIVACY_COMPLIANCE.md) for full policy.
