# API CONTRACTS — AI Visibility SaaS

**Base URL:** `https://api.aivisibility.app/v1`  
**Auth:** `Authorization: Bearer <jwt_token>`  
**Content-Type:** `application/json`  
**Version:** v1 (current)  
**Last Updated:** 2026-02-27

---

## Versioning Policy

- API version is path-prefixed: `/v1/...`
- Breaking changes increment the version: `/v2/...`
- Non-breaking additions (new optional fields) are made in-place
- Deprecation notice: 90 days with `Deprecation` response header
- Old versions supported for 6 months after new version launch

---

## Idempotency

- All `POST` endpoints accept an optional `Idempotency-Key` header (UUID)
- Duplicate requests with the same key within 24 hours return the original response (status 200) without re-processing
- Store and check idempotency keys server-side in Redis with 24h TTL

---

## Retry Policy

- Client should retry on `429` and `5xx` with exponential backoff
- Recommended: 3 retries, initial delay 1s, max delay 30s, jitter ±20%
- `503` with `Retry-After` header: respect the header value

---

## Common Response Envelope

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2026-02-27T15:30:00Z"
  }
}
```

**On error:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": [ ... ]
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2026-02-27T15:30:00Z"
  }
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|---|---|---|
| `VALIDATION_ERROR` | 400 | Request body failed schema validation |
| `UNAUTHORIZED` | 401 | Missing or invalid JWT token |
| `FORBIDDEN` | 403 | Token valid but insufficient workspace permissions |
| `NOT_FOUND` | 404 | Resource does not exist or is not accessible |
| `CONFLICT` | 409 | Idempotent request conflict (duplicate key, different payload) |
| `RATE_LIMITED` | 429 | Too many requests; see `Retry-After` header |
| `PROVIDER_ERROR` | 502 | Upstream LLM provider returned an error |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `SERVICE_UNAVAILABLE` | 503 | Planned maintenance or overload |

---

## Endpoints

---

### `POST /visibility/run`

Trigger a new AI visibility run for a keyword.

**Request:**

```json
{
  "keywordId": "kw_01HZ...",          // required, existing keyword ID
  "providers": ["chatgpt", "gemini", "perplexity"], // required, min 1
  "promptVariantCount": 10,           // optional, default 10, range 1-50
  "brandDictionaryId": "bd_01HZ...", // optional, uses workspace default if omitted
  "notify": {
    "webhookUrl": "https://hooks.example.com/ai-vis" // optional
  }
}
```

**Response `201 Created`:**

```json
{
  "success": true,
  "data": {
    "runId": "run_01HZ...",
    "status": "QUEUED",
    "keywordId": "kw_01HZ...",
    "providers": ["chatgpt", "gemini", "perplexity"],
    "promptVariantCount": 10,
    "estimatedCompletionSeconds": 45,
    "createdAt": "2026-02-27T15:30:00Z"
  }
}
```

**Field rules:**
- `providers`: allowed values `chatgpt`, `gemini`, `perplexity`
- `promptVariantCount`: integer 1–50; higher values increase cost and latency
- If `keywordId` belongs to a different workspace than the token, returns `FORBIDDEN`

---

### `GET /runs/:id`

Get the status and results of a visibility run.

**Path params:** `id` — run ID (`run_01HZ...`)

**Response `200 OK` (run in progress):**

```json
{
  "success": true,
  "data": {
    "runId": "run_01HZ...",
    "status": "RUNNING",
    "progress": {
      "completedProviders": ["chatgpt"],
      "pendingProviders": ["gemini", "perplexity"],
      "promptsCompleted": 10,
      "promptsTotal": 30
    },
    "createdAt": "2026-02-27T15:30:00Z",
    "updatedAt": "2026-02-27T15:30:22Z"
  }
}
```

**Response `200 OK` (run completed):**

```json
{
  "success": true,
  "data": {
    "runId": "run_01HZ...",
    "status": "COMPLETED",
    "keywordId": "kw_01HZ...",
    "keyword": "best CRM for startups",
    "createdAt": "2026-02-27T15:30:00Z",
    "completedAt": "2026-02-27T15:31:02Z",
    "summary": {
      "sov": 0.43,                  // Share of Voice: 43% of responses mention brand
      "top1Rate": 0.21,             // 21% of responses, brand is first mention
      "sentimentBreakdown": {
        "positive": 0.60,
        "neutral": 0.30,
        "negative": 0.10
      },
      "totalPrompts": 30,
      "totalResponses": 30
    },
    "providerResults": [
      {
        "provider": "chatgpt",
        "sov": 0.50,
        "top1Rate": 0.30,
        "promptsRun": 10,
        "mentionCount": 5,
        "avgSentiment": "positive",
        "citations": []
      },
      {
        "provider": "gemini",
        "sov": 0.40,
        "top1Rate": 0.20,
        "promptsRun": 10,
        "mentionCount": 4,
        "avgSentiment": "neutral",
        "citations": []
      },
      {
        "provider": "perplexity",
        "sov": 0.40,
        "top1Rate": 0.10,
        "promptsRun": 10,
        "mentionCount": 4,
        "avgSentiment": "positive",
        "citations": [
          { "url": "https://example.com/blog/crm-guide", "count": 3 }
        ]
      }
    ],
    "competitorSov": [
      { "brand": "Competitor A", "sov": 0.67 },
      { "brand": "Competitor B", "sov": 0.53 }
    ]
  }
}
```

**Status values:** `QUEUED` | `RUNNING` | `COMPLETED` | `FAILED` | `CANCELLED`

---

### `GET /runs`

List runs for the authenticated workspace.

**Query params:**

| Param | Type | Default | Description |
|---|---|---|---|
| `keywordId` | string | — | Filter by keyword |
| `status` | string | — | Filter by status |
| `limit` | integer | 20 | Max records (1–100) |
| `cursor` | string | — | Pagination cursor |
| `sort` | string | `createdAt:desc` | Sort field and direction |

**Response `200 OK`:**

```json
{
  "success": true,
  "data": {
    "runs": [ { ... } ],
    "nextCursor": "cursor_xyz",
    "total": 142
  }
}
```

---

### `POST /gap/run`

Trigger a gap analysis between brand and competitors for a keyword.

**Request:**

```json
{
  "keywordId": "kw_01HZ...",
  "runId": "run_01HZ...",           // optional: base on a specific run
  "competitors": ["Competitor A", "Competitor B"],
  "depth": "standard"               // "standard" | "deep"
}
```

**Response `201 Created`:**

```json
{
  "success": true,
  "data": {
    "gapRunId": "gap_01HZ...",
    "status": "QUEUED",
    "estimatedCompletionSeconds": 30,
    "createdAt": "2026-02-27T15:35:00Z"
  }
}
```

---

### `GET /gap/:id`

Get results of a gap analysis run.

**Response `200 OK` (completed):**

```json
{
  "success": true,
  "data": {
    "gapRunId": "gap_01HZ...",
    "status": "COMPLETED",
    "keyword": "best CRM for startups",
    "brandSov": 0.43,
    "gaps": [
      {
        "competitor": "Competitor A",
        "competitorSov": 0.67,
        "sovGap": 0.24,
        "topMissingTopics": [
          "integration with Slack",
          "pricing transparency",
          "mobile app support"
        ],
        "recommendedActions": [
          "Publish a detailed Slack integration guide",
          "Add a public pricing page"
        ]
      }
    ],
    "completedAt": "2026-02-27T15:35:28Z"
  }
}
```
