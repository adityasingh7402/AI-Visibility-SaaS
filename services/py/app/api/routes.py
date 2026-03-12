"""
GEO Platform — API Routes
POST /analyze      — Full page analysis
POST /analyze-keyword — Keyword-only analysis
GET  /health       — Health check (in main.py)
"""

import time

import structlog
from fastapi import APIRouter

from app.models.analysis import AnalyzeKeywordRequest, AnalyzeRequest, AnalyzeResponse

log = structlog.get_logger()
router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_page(request: AnalyzeRequest):
    """Full GEO analysis — crawl page + research + test LLMs + optimize.

    Steps:
      1. Validate request
      2. Run 6-agent LangGraph pipeline
      3. Return complete report

    Called by Node.js service with HMAC auth.
    """
    start = time.perf_counter()

    log.info(
        "analysis_started",
        url=request.url,
        brand=request.brand_name,
        providers=request.providers,
    )

    # TODO: Phase 7 — Wire up LangGraph pipeline
    # For now, return a structured placeholder
    elapsed = time.perf_counter() - start

    return AnalyzeResponse(
        url=request.url,
        brand_name=request.brand_name,
        executive_summary="Analysis pipeline not yet connected. Phase 7 integration pending.",
        geo_score={
            "overall": 0,
            "sub_scores": {
                "web_presence": 0,
                "authority": 0,
                "llm_mention": 0,
                "page_quality": 0,
                "technical_seo": 0,
                "image_seo": 0,
                "competitor_gap": 0,
            },
            "grade": "F",
        },
        processing_time_seconds=round(elapsed, 2),
    )


@router.post("/analyze-keyword", response_model=AnalyzeResponse)
async def analyze_keyword(request: AnalyzeKeywordRequest):
    """Keyword-only analysis — no page crawl, just LLM testing.

    Used when customer wants to test a keyword without a specific URL.
    """
    start = time.perf_counter()

    log.info(
        "keyword_analysis_started",
        keyword=request.keyword,
        brand=request.brand_name,
        providers=request.providers,
    )

    # TODO: Phase 7 — Wire up keyword-only pipeline
    elapsed = time.perf_counter() - start

    return AnalyzeResponse(
        url="",
        brand_name=request.brand_name,
        executive_summary="Keyword analysis pipeline not yet connected.",
        geo_score={
            "overall": 0,
            "sub_scores": {
                "web_presence": 0,
                "authority": 0,
                "llm_mention": 0,
                "page_quality": 0,
                "technical_seo": 0,
                "image_seo": 0,
                "competitor_gap": 0,
            },
            "grade": "F",
        },
        processing_time_seconds=round(elapsed, 2),
    )
