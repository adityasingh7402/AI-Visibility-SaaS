# ============================================================
# GEO Platform — Multi-stage Docker Build
# Stage 1: Install deps with uv (fast)
# Stage 2: Slim runtime image
# ============================================================

FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install uv

# Copy dependency manifest first (layer cache optimization)
COPY pyproject.toml .
RUN uv pip install --system --no-cache-dir .

# Download spaCy model (sm = 15MB — instructor is primary extractor, spaCy is backup)
RUN python -m spacy download en_core_web_sm

# ---

FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Non-root user for security
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
