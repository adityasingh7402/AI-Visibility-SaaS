"""
GEO Platform — Agent Output Schemas
Each agent produces a typed result stored in LangGraph shared state.
"""

from datetime import datetime

from pydantic import BaseModel, Field


# ============================================================
# AGENT 1: Crawler Output
# ============================================================

class PageMeta(BaseModel):
    """Extracted meta information from the page."""

    title: str = ""
    description: str = ""
    canonical_url: str = ""
    language: str = ""
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""


class PageImage(BaseModel):
    """Single image extracted from the page."""

    src: str
    alt: str = ""
    file_name: str = ""
    width: int | None = None
    height: int | None = None


class HeadingStructure(BaseModel):
    """Page heading hierarchy."""

    h1: list[str] = []
    h2: list[str] = []
    h3: list[str] = []


class CrawlResult(BaseModel):
    """Agent 1 output — everything extracted from the page."""

    url: str
    status_code: int = 200
    title: str = ""
    meta: PageMeta = Field(default_factory=PageMeta)
    headings: HeadingStructure = Field(default_factory=HeadingStructure)
    body_text: str = Field(default="", description="Full text content")
    word_count: int = 0
    images: list[PageImage] = []
    internal_links: list[str] = []
    external_links: list[str] = []
    schema_org: list[dict] = Field(default=[], description="JSON-LD structured data")
    what_ai_sees: str = Field(default="", description="Stripped, text-only view")
    crawl_method: str = Field(default="httpx", description="httpx or crawl4ai")
    error: str | None = None


# ============================================================
# AGENT 2: Researcher Output
# ============================================================

class CompetitorInfo(BaseModel):
    """Discovered competitor with validation."""

    name: str
    url: str = ""
    is_customer_provided: bool = False
    relevance_score: float = Field(default=0.0, ge=0, le=1)


class WebPresenceEntry(BaseModel):
    """Single web presence data point."""

    source: str = Field(..., description="e.g., 'Wikipedia', 'G2', 'Forbes'")
    found: bool = False
    url: str = ""
    details: str = ""


class ResearchResult(BaseModel):
    """Agent 2 output — competitor intel + web presence."""

    product_understanding: str = Field(default="", description="What the product does")
    category: str = Field(default="", description="Product category extracted")
    competitors: list[CompetitorInfo] = []
    keyword_gaps: list[str] = Field(default=[], description="Keywords competitors use")
    trending_topics: list[str] = []
    web_presence: list[WebPresenceEntry] = []
    web_presence_score: float = Field(default=0.0, ge=0, le=100)
    authority_score: float = Field(default=0.0, ge=0, le=100)
    error: str | None = None


# ============================================================
# AGENT 3: LLM Tester Output
# ============================================================

class MentionDetail(BaseModel):
    """Single mention instance in an LLM response."""

    text_snippet: str = Field(default="", description="Surrounding text context")
    position: int = Field(default=0, description="Rank position (1=first mentioned)")
    sentiment: str = Field(default="neutral", description="positive/neutral/negative")


class SingleRunResult(BaseModel):
    """Result of a single LLM test run."""

    mentioned: bool = False
    position: int | None = None
    mentions: list[MentionDetail] = []
    raw_response: str = ""


class PromptTestResult(BaseModel):
    """Aggregated result for one prompt across 5 runs."""

    prompt_text: str
    prompt_style: str
    runs: list[SingleRunResult] = []
    mention_rate: float = Field(default=0.0, description="X/5 = mentioned X% of time")
    avg_position: float | None = None
    consistency: str = Field(default="low", description="high/medium/low")


class LLMProviderResult(BaseModel):
    """Agent 3 output — per-provider visibility test results."""

    provider: str = Field(..., description="Provider ID from registry")
    model_name: str = Field(..., description="Human-readable name shown to customer")
    model_id: str = Field(..., description="Internal model ID")
    tested_at: datetime = Field(default_factory=datetime.utcnow)

    # Aggregated across all prompts and runs
    mention_rate: float = Field(default=0.0, description="Overall mention rate (0-1)")
    average_position: float | None = None
    sentiment: str = Field(default="neutral")
    share_of_voice: float = Field(default=0.0, description="SOV percentage")
    prompt_results: list[PromptTestResult] = []
    raw_responses: list[str] = Field(default=[], description="All raw LLM responses")

    # NOTE: No api_cost field — costs not shown to customer


# ============================================================
# AGENT 4: Image Analyzer Output
# ============================================================

class ImageAnalysis(BaseModel):
    """Analysis of a single page image."""

    src: str
    current_alt: str = ""
    suggested_alt: str = ""
    alt_quality_score: float = Field(default=0.0, ge=0, le=100)
    content_description: str = Field(default="", description="What the image shows")
    relevance_score: float = Field(default=0.0, ge=0, le=100, description="Image vs page relevance")
    file_name_suggestion: str = ""


class ImageAnalysisResult(BaseModel):
    """Agent 4 output — all images analyzed."""

    images: list[ImageAnalysis] = []
    overall_image_score: float = Field(default=0.0, ge=0, le=100)
    error: str | None = None
