"""
GEO Platform — Confidence & Content Schemas
Recommendations, battle cards, generated content, and citation sources.
"""

from pydantic import BaseModel, Field


# ============================================================
# CONFIDENCE-LABELED RECOMMENDATIONS
# ============================================================

class Recommendation(BaseModel):
    """Single recommendation with confidence label and evidence."""

    title: str = Field(..., description="Short action title")
    description: str = Field(..., description="What to do and why")
    confidence: str = Field(..., description="HIGH / MEDIUM / LOW")
    evidence: list[str] = Field(default=[], description="Data points supporting this")
    category: str = Field(default="content", description="content/technical/authority/image")
    priority: int = Field(default=5, ge=1, le=10, description="1=highest priority")
    estimated_impact: str = Field(default="", description="Expected improvement")


# ============================================================
# GENERATED CONTENT (copy-paste ready)
# ============================================================

class GeneratedFAQ(BaseModel):
    """Single FAQ entry — answer-first format."""

    question: str
    answer: str = Field(..., description="50-word direct answer first, then detail")


class GeneratedContent(BaseModel):
    """Agent 5 output — all generated content for the customer."""

    faqs: list[GeneratedFAQ] = Field(default=[], description="5-8 AI-optimized Q&As")
    meta_title: str = Field(default="", description="Optimized title tag")
    meta_description: str = Field(default="", description="Optimized meta description")
    product_description: str = Field(default="", description="Rewritten product desc with keywords")
    missing_sections: list[dict] = Field(default=[], description="Content for identified gaps")
    image_alt_texts: dict[str, str] = Field(default={}, description="src → suggested alt text")
    blog_outline: dict = Field(default={}, description="Blog post outline for content gaps")
    schema_markup: str = Field(default="", description="FAQPage JSON-LD code")


# ============================================================
# BATTLE CARDS
# ============================================================

class BattleCard(BaseModel):
    """Auto-generated competitive intelligence card."""

    competitor_name: str
    competitor_url: str = ""
    ai_positioning: str = Field(default="", description="How AI positions this competitor")
    strengths: list[str] = []
    weaknesses: list[str] = []
    keyword_gaps: list[str] = Field(default=[], description="Keywords they have, we don't")
    web_presence_comparison: dict = Field(default={}, description="Side-by-side presence data")
    suggested_comparison_page: str = Field(default="", description="Draft comparison page")


# ============================================================
# AI-READY CONTENT TIPS
# ============================================================

class AIReadyTips(BaseModel):
    """Industry-specific tips for writing AI-friendly content."""

    format_tips: list[str] = Field(default=[], description="Q&A, lists, structured data")
    keyword_tips: list[str] = Field(default=[], description="Where to place keywords")
    authority_tips: list[str] = Field(default=[], description="How to build authority signals")
    common_mistakes: list[str] = Field(default=[], description="What to avoid")
    industry_specific: list[str] = Field(default=[], description="Tips for this vertical")


# ============================================================
# CITATION SOURCE TRACING (Innovation 5)
# ============================================================

class CitationSource(BaseModel):
    """Explains WHY a competitor ranks higher in AI responses."""

    competitor_name: str
    ai_platform: str = Field(..., description="Which AI mentioned them")
    likely_reasons: list[str] = Field(
        default=[], description="Wikipedia page, G2 reviews, Forbes mention, etc."
    )
    fix_suggestions: list[str] = Field(
        default=[], description="Actionable steps to close the gap"
    )
    priority_fix: str = Field(default="", description="Single highest-impact action")
