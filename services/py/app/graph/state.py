"""
GEO Platform — LangGraph Shared State
All data flows between agents through this typed state.
"""

from typing import Annotated

from langgraph.graph import add_messages
from pydantic import BaseModel, Field

from app.models.agents import CrawlResult, ImageAnalysisResult, LLMProviderResult, ResearchResult
from app.models.analysis import AnalyzeRequest, GEOScore
from app.models.confidence import (
    AIReadyTips,
    BattleCard,
    CitationSource,
    GeneratedContent,
    Recommendation,
)


class AnalysisState(BaseModel):
    """Shared state passed between all 6 agents in the LangGraph pipeline.

    Flow: Request → Agent 1 → Agents 2,3,4 (parallel) → Agent 5 → Agent 6 → Response
    """

    # --- Input ---
    request: AnalyzeRequest

    # --- Agent 1: Crawler ---
    crawl_result: CrawlResult | None = None

    # --- Agent 2: Researcher ---
    research_result: ResearchResult | None = None

    # --- Agent 3: LLM Tester ---
    llm_results: list[LLMProviderResult] = []

    # --- Agent 4: Image Analyzer ---
    image_result: ImageAnalysisResult | None = None

    # --- Agent 5: Optimizer ---
    geo_score: GEOScore | None = None
    recommendations: list[Recommendation] = []
    generated_content: GeneratedContent | None = None
    battle_cards: list[BattleCard] = []
    ai_ready_tips: AIReadyTips | None = None
    citation_sources: list[CitationSource] = []
    executive_summary: str = ""

    # --- Agent 6: Verifier ---
    quality_check_passed: bool = False
    verifier_retries: int = 0
    verifier_feedback: str = ""

    # --- Metadata ---
    errors: list[str] = Field(default=[], description="Non-fatal errors from agents")
