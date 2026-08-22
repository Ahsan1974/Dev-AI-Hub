"""Transparent data-quality score.

The number is not a rating of the tool - it measures how complete and how fresh
*our record* of the tool is. Every component is returned so the UI can show why.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel

from app.core.enums import FREE_PRICING_STATUSES, TagKind
from app.models.tool import Tool


class QualityComponent(BaseModel):
    key: str
    label: str
    score: float
    max_score: float


class QualityScore(BaseModel):
    score: int
    max_score: int = 100
    components: list[QualityComponent]


def compute_quality_score(tool: Tool) -> QualityScore:
    completeness = 0.0
    for present in (
        bool(tool.description),
        bool(tool.long_description),
        bool(tool.best_for),
        bool(tool.capabilities),
        bool(tool.logo_url or tool.website_url),
        bool(tool.categories),
    ):
        completeness += 30 / 6 if present else 0

    free_availability = 0.0
    if tool.pricing_status in FREE_PRICING_STATUSES:
        free_availability += 15
    if tool.free_access_grants:
        free_availability += 10
    free_availability = min(free_availability, 25)

    tech_tags = [t for t in tool.tags if t.kind == TagKind.TECHNOLOGY]
    feature_tags = [t for t in tool.tags if t.kind == TagKind.FEATURE]
    relevance = min(len(tech_tags), 5) * 2 + min(len(feature_tags), 5) * 2
    relevance = min(relevance, 20)

    freshness = 0.0
    if tool.last_verified_at:
        reference = tool.last_verified_at
        if reference.tzinfo is None:
            reference = reference.replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - reference).days
        if age_days <= 90:
            freshness = 15
        elif age_days <= 180:
            freshness = 10
        elif age_days <= 365:
            freshness = 5

    pricing_clarity = 0.0
    if tool.pricing_plans:
        pricing_clarity += 6
    if tool.pricing_summary:
        pricing_clarity += 2
    if tool.verification_source_url:
        pricing_clarity += 2
    pricing_clarity = min(pricing_clarity, 10)

    components = [
        QualityComponent(
            key="completeness",
            label="Data completeness",
            score=round(completeness, 1),
            max_score=30,
        ),
        QualityComponent(
            key="free_availability",
            label="Free availability detail",
            score=free_availability,
            max_score=25,
        ),
        QualityComponent(
            key="developer_relevance",
            label="Developer relevance",
            score=relevance,
            max_score=20,
        ),
        QualityComponent(
            key="verification_freshness",
            label="Verification freshness",
            score=freshness,
            max_score=15,
        ),
        QualityComponent(
            key="pricing_clarity",
            label="Pricing clarity",
            score=pricing_clarity,
            max_score=10,
        ),
    ]
    total = round(sum(component.score for component in components))
    return QualityScore(score=int(total), components=components)
