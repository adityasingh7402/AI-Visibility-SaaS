"""
GEO Platform — FastAPI Application
Main entrypoint with health check, logging setup, and CORS.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings


def setup_logging() -> None:
    """Configure structlog for JSON-formatted logging."""
    settings = get_settings()

    import logging

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            # dev: pretty console, prod: JSON
            structlog.dev.ConsoleRenderer()
            if settings.is_dev
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def setup_langfuse() -> None:
    """Wire LangFuse into LiteLLM for LLM call tracing."""
    import os

    import litellm

    settings = get_settings()

    if settings.langfuse_public_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
        os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
        os.environ["LANGFUSE_HOST"] = settings.langfuse_host

        litellm.success_callback = ["langfuse"]
        litellm.failure_callback = ["langfuse"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown — init logging, LangFuse, and heavy models."""
    log = structlog.get_logger()

    # --- Startup ---
    setup_logging()
    setup_langfuse()
    log.info("geo_platform_starting", env=get_settings().app_env)

    yield

    # --- Shutdown ---
    log.info("geo_platform_stopping")


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="GEO Platform — AI Visibility Engine",
        version="0.1.0",
        description="Generative Engine Optimization analysis service",
        docs_url="/docs" if settings.is_dev else None,
        lifespan=lifespan,
    )

    # CORS — Node.js backend calls us
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )

    # Security — HMAC auth + request tracing
    from app.api.middleware import HMACAuthMiddleware, RequestIdMiddleware

    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(HMACAuthMiddleware)

    # Routes
    from app.api.routes import router

    app.include_router(router)

    # Health check (no auth needed)
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "geo-platform", "version": "0.1.0"}

    return app


# Uvicorn entrypoint
app = create_app()
