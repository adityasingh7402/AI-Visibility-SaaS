"""
GEO Platform — Test Configuration & Shared Fixtures
Reusable test data and mocked dependencies.
"""

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


# --- App Fixtures ---

@pytest.fixture
def settings():
    """Test settings with dummy keys."""
    return Settings(
        app_env="testing",
        groq_api_key_1="test-groq-key-1",
        groq_api_key_2="test-groq-key-2",
        fireworks_api_key="test-fireworks-key",
        mistral_api_key="test-mistral-key",
        google_api_key="test-google-key",
        openai_api_key="test-openai-key",
        hmac_secret_key="test-hmac-secret",
    )


@pytest.fixture
def app():
    """Fresh FastAPI app for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Test client — no HMAC auth for unit tests."""
    return TestClient(app)


# --- Sample Data Fixtures ---

@pytest.fixture
def sample_analyze_request():
    """Minimal valid AnalyzeRequest."""
    return {
        "url": "https://freshbooks.com/invoicing",
        "brand_name": "FreshBooks",
        "aliases": ["FB", "Fresh Books"],
        "competitors": ["QuickBooks", "Xero"],
        "providers": ["chatgpt", "gemini"],
    }


@pytest.fixture
def sample_keyword_request():
    """Minimal valid AnalyzeKeywordRequest."""
    return {
        "keyword": "best invoicing software",
        "brand_name": "FreshBooks",
        "competitors": ["QuickBooks"],
        "providers": ["chatgpt"],
    }


@pytest.fixture
def sample_crawl_result():
    """Realistic CrawlResult for testing downstream agents."""
    return {
        "url": "https://freshbooks.com/invoicing",
        "status_code": 200,
        "title": "FreshBooks Invoicing Software",
        "meta": {
            "title": "FreshBooks Invoicing",
            "description": "Send invoices in seconds",
            "canonical_url": "https://freshbooks.com/invoicing",
        },
        "headings": {
            "h1": ["FreshBooks Invoicing"],
            "h2": ["Features", "Pricing", "FAQ"],
            "h3": ["Automated Billing", "Time Tracking"],
        },
        "body_text": "FreshBooks is the #1 invoicing software for small businesses...",
        "word_count": 1500,
        "images": [
            {
                "src": "https://freshbooks.com/img/hero.png",
                "alt": "FreshBooks dashboard",
                "file_name": "hero.png",
            }
        ],
        "schema_org": [],
        "crawl_method": "httpx",
    }
