"""
GEO Platform — Analysis Schemas
Request/response contracts between Node.js and our Python service.
"""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


# ============================================================
# REQUEST — What the customer sends (via Node.js)
# ============================================================

class AnalyzeRequest(BaseModel):
    """Input from Node.js — customer's analysis request."""

    url: str = Field(..., description="Page URL to analyze")
    brand_name: str = Field(..., description="Brand to track visibility for")
    aliases: list[str] = Field(default=[], description="Brand name variations (e.g., 'FB' for FreshBooks)")
    competitors: list[str] = Field(default=[], description="Known competitors to track")

    # Customer picks which LLMs to test
    providers: list[str] = Field(
        default=["chatgpt", "gemini", "perplexity"],
        description="Provider IDs from providers_registry.yaml",
    )
    # Optional: pin specific model version
    models: dict[str, str] | None = Field(
        default=None,
        description="Override model per provider: {'chatgpt': 'gpt-5'}",
    )


class AnalyzeKeywordRequest(BaseModel):
    """Keyword-only mode — no URL, just brand + keyword."""

    keyword: str = Field(..., description="Search keyword to test")
    brand_name: str
    aliases: list[str] = []
    competitors: list[str] = []
    providers: list[str] = ["chatgpt", "gemini", "perplexity"]
    models: dict[str, str] | None = None


# ============================================================
# GEO SCORE — 7 weighted sub-scores
# ============================================================

class GEOSubScores(BaseModel):
    """Individual components that make up the GEO Score."""

    web_presence: float = Field(..., ge=0, le=100, description="Wikipedia, G2, authority sites")
    authority: float = Field(..., ge=0, le=100, description="Forbes, TechCrunch, review sites")
    llm_mention: float = Field(..., ge=0, le=100, description="How often AI mentions the brand")
    page_quality: float = Field(..., ge=0, le=100, description="Content structure, answer-first")
    technical_seo: float = Field(..., ge=0, le=100, description="Meta, schema, headings")
    image_seo: float = Field(..., ge=0, le=100, description="Alt text, file names, relevance")
    competitor_gap: float = Field(..., ge=0, le=100, description="Gap vs top competitors")


class GEOScore(BaseModel):
    """GEO Score™ — 0-100 with 7 weighted sub-scores."""

    overall: float = Field(..., ge=0, le=100, description="Weighted final score")
    sub_scores: GEOSubScores
    grade: str = Field(..., description="A/B/C/D/F grade")

    # Weight config (for transparency in report)
    weights: dict[str, float] = Field(
        default={
            "web_presence": 0.20,
            "authority": 0.20,
            "llm_mention": 0.20,
            "page_quality": 0.15,
            "technical_seo": 0.10,
            "image_seo": 0.05,
            "competitor_gap": 0.10,
        }
    )


# ============================================================
# RESPONSE — Full analysis report (NO cost fields)
# ============================================================

class AnalyzeResponse(BaseModel):
    """Final report sent back to Node.js → customer."""

    # --- Core ---
    url: str
    brand_name: str
    executive_summary: str = Field(..., description="CMO-readable plain-English summary")
    geo_score: GEOScore

    # --- Detailed Results (imported from agents.py / confidence.py) ---
    # These are list/model types defined in their respective files.
    # Kept as dict/list here for now — typed in Phase 6 integration.
    recommendations: list[dict] = Field(default=[], description="Confidence-labeled recommendations")
    generated_content: dict = Field(default={}, description="Copy-paste ready content")
    battle_cards: list[dict] = Field(default=[], description="Per-competitor battle cards")
    ai_ready_tips: dict = Field(default={}, description="Content format tips for AI")
    llm_visibility: list[dict] = Field(default=[], description="Per-provider results")
    web_presence: dict = Field(default={}, description="Authority + web presence data")
    image_analysis: dict = Field(default={}, description="Per-image analysis")
    page_audit: dict = Field(default={}, description="Technical page data")
    what_ai_sees: str = Field(default="", description="Stripped text-only view")
    citation_sources: list[dict] = Field(default=[], description="WHY competitors rank higher")

    # --- Metadata ---
    processing_time_seconds: float = 0.0
    quality_check_passed: bool = False
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

    # --- Temporal (Phase 9) ---
    previous_scores: list[dict] | None = Field(
        default=None, description="Historical GEO scores if available"
    )

    # NOTE: NO cost fields — API costs are not shown to customers
