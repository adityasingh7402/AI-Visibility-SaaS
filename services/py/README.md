# GEO Platform — Python AI Service

AI Visibility Analysis Engine for Generative Engine Optimization.

## Quick Start

```bash
# Install dependencies
uv pip install --system -e ".[dev]"

# Run locally
uvicorn app.main:app --reload --port 8000

# Run tests
pytest tests/ -v
```

## Endpoints

- `GET /health` — Health check
- `POST /analyze` — Full page GEO analysis
- `POST /analyze-keyword` — Keyword-only analysis
