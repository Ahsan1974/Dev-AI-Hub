from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.core.enums import Budget
from app.schemas.tool import ToolSummary, ToolWithScore


class RecommendationRequest(BaseModel):
    """Payload of the "What do I need?" flow."""

    query: str = Field(
        min_length=3,
        max_length=1000,
        description="Free text task description.",
        examples=["I need a free AI tool to generate Java unit tests"],
    )
    budget: Budget = Budget.MOSTLY_FREE
    technologies: list[str] = Field(default_factory=list, max_length=20)
    categories: list[str] = Field(default_factory=list, max_length=20)
    limit: int = Field(default=8, ge=1, le=24)


class RecommendationMeta(BaseModel):
    strategy: Literal["rule_based_scoring", "llm_reranked"] = "rule_based_scoring"
    interpreted_keywords: list[str] = Field(default_factory=list)
    detected_categories: list[str] = Field(default_factory=list)
    detected_technologies: list[str] = Field(default_factory=list)
    detected_features: list[str] = Field(default_factory=list)
    budget: str = Budget.MOSTLY_FREE
    candidates_considered: int = 0
    scoring_weights: dict[str, int] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    best_match: ToolWithScore | None = None
    other_options: list[ToolWithScore] = Field(default_factory=list)
    meta: RecommendationMeta


class StackRequest(BaseModel):
    """Payload of "Build my stack"."""

    primary_language: str | None = Field(default=None, max_length=60)
    frameworks: list[str] = Field(default_factory=list, max_length=10)
    ide: str | None = Field(default=None, max_length=60)
    goals: list[str] = Field(default_factory=list, max_length=12)
    budget: Budget = Budget.FREE_ONLY
    include_areas: list[str] = Field(default_factory=list, max_length=15)


class StackSlot(BaseModel):
    area: str
    slug: str
    description: str
    picks: list[ToolWithScore] = Field(default_factory=list)


class StackResponse(BaseModel):
    slots: list[StackSlot]
    summary: str
    explanation: list[str] = Field(default_factory=list)
    unmatched_areas: list[str] = Field(default_factory=list)


class AlternativesResponse(BaseModel):
    data: list[ToolSummary]
    meta: dict
