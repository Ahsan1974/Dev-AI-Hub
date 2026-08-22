"""Contract for the future research agent.

    scheduler -> research agent -> web search -> candidate tools
    -> official website check -> extract metadata -> pricing verification
    -> quality scoring -> admin approval -> database

Candidates always land in ``PENDING_REVIEW``. Automatic publication is
deliberately impossible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.core.config import settings


class DiscoveryStage(StrEnum):
    SEARCH = "search"
    FETCH = "fetch"
    EXTRACT = "extract"
    VERIFY_PRICING = "verify_pricing"
    SCORE = "score"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"


@dataclass(slots=True)
class CandidateTool:
    name: str
    website_url: str
    source: str
    stage: DiscoveryStage = DiscoveryStage.SEARCH
    evidence: list[str] = field(default_factory=list)
    extracted: dict = field(default_factory=dict)
    quality_score: int = 0
    discovered_at: datetime | None = None


@dataclass(slots=True)
class PricingChange:
    """Emitted when a verification run sees different numbers than stored."""

    tool_slug: str
    field: str
    old_value: str | None
    new_value: str | None
    source_url: str
    detected_at: datetime


class DiscoveryPipeline:
    """Not implemented in V1; documents the intended flow and its guard rails."""

    def __init__(self) -> None:
        self.enabled = settings.web_search_enabled

    async def discover(self, topic: str) -> list[CandidateTool]:
        if not self.enabled:
            return []
        raise NotImplementedError(
            "Automated discovery is not implemented in V1. Enable a web search "
            "provider and implement the search -> verify -> review stages."
        )

    async def verify_pricing(self, tool_slug: str) -> list[PricingChange]:
        raise NotImplementedError(
            "Pricing verification is not implemented in V1. It must write a "
            "PricingChange record and leave the stored values untouched until an "
            "administrator approves the change."
        )
