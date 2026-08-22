"""Rule-based recommendation engine.

No LLM and no API key required. The pipeline is intentionally split into
``extract intent -> retrieve candidates -> score -> explain`` so an LLM re-ranker
can be inserted between "retrieve" and "explain" later (see
``app.services.llm``).
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import FREE_PRICING_STATUSES, Budget, PricingStatus, TagKind
from app.models.tool import Tool
from app.repositories.category_repository import CategoryRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.tool_repository import ToolRepository
from app.schemas.recommendation import (
    RecommendationMeta,
    RecommendationRequest,
    RecommendationResponse,
)
from app.schemas.tool import ToolSummary, ToolWithScore
from app.services.intent import Intent, TaxonomyIndex, extract_intent
from app.utils.text import singularize

WEIGHTS: dict[str, int] = {
    "category": 30,
    "keyword": 25,
    "technology": 20,
    "feature": 15,
    "pricing": 10,
}

#: Below this a result is noise rather than a recommendation.
MIN_SCORE = 20

_BUDGET_PRICING_SCORE: dict[str, dict[str, float]] = {
    Budget.FREE_ONLY: {
        PricingStatus.FREE_FOREVER: 1.0,
        PricingStatus.OPEN_SOURCE: 1.0,
        PricingStatus.FREE_TIER: 0.9,
        PricingStatus.BYOK: 0.8,
        PricingStatus.FREE_CREDITS: 0.7,
        PricingStatus.FREE_TRIAL: 0.0,
        PricingStatus.PAID_ONLY: 0.0,
    },
    Budget.MOSTLY_FREE: {
        PricingStatus.FREE_FOREVER: 1.0,
        PricingStatus.OPEN_SOURCE: 1.0,
        PricingStatus.FREE_TIER: 1.0,
        PricingStatus.BYOK: 0.9,
        PricingStatus.FREE_CREDITS: 0.85,
        PricingStatus.FREE_TRIAL: 0.4,
        PricingStatus.PAID_ONLY: 0.15,
    },
}


@dataclass(slots=True)
class ScoredTool:
    tool: Tool
    score: int
    reasons: list[str]
    matched_categories: list[str]
    matched_technologies: list[str]
    matched_features: list[str]

    def to_schema(self) -> ToolWithScore:
        return ToolWithScore(
            tool=ToolSummary.from_model(self.tool),
            score=self.score,
            reasons=self.reasons,
            matched_categories=self.matched_categories,
            matched_technologies=self.matched_technologies,
            matched_features=self.matched_features,
        )


def _tag_slugs(tool: Tool, kind: str) -> set[str]:
    return {tag.slug for tag in tool.tags if tag.kind == kind}


def _tag_names(tool: Tool, kind: str, slugs: set[str]) -> list[str]:
    return [tag.name for tag in tool.tags if tag.kind == kind and tag.slug in slugs]


class RecommendationService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.tools = ToolRepository(session)
        self.categories = CategoryRepository(session)
        self.tags = TagRepository(session)

    async def taxonomy(self) -> TaxonomyIndex:
        categories = await self.categories.list_all()
        tags = await self.tags.list_all()
        return TaxonomyIndex(categories, tags)

    # ---------------------------------------------------------------- scoring

    def _keyword_score(self, tool: Tool, intent: Intent) -> tuple[float, list[str]]:
        if not intent.keywords:
            return 0.0, []
        haystack = tool.search_text.lower()
        name = f"{tool.name} {tool.tagline}".lower()
        hits: list[str] = []
        weight = 0.0
        for word in intent.keywords:
            stem = singularize(word)
            if word in name or stem in name:
                weight += 1.5
                hits.append(word)
            elif word in haystack or stem in haystack:
                weight += 1.0
                hits.append(word)
        return min(weight / len(intent.keywords), 1.0), hits

    def _pricing_score(self, tool: Tool, budget: str) -> float:
        table = _BUDGET_PRICING_SCORE.get(budget)
        if table is None:
            return 1.0
        return table.get(tool.pricing_status, 0.0)

    def score_tool(
        self, tool: Tool, intent: Intent, budget: str
    ) -> ScoredTool | None:
        tool_categories = {category.slug for category in tool.categories}
        tool_tech = _tag_slugs(tool, TagKind.TECHNOLOGY)
        tool_features = _tag_slugs(tool, TagKind.FEATURE)

        matched_categories = tool_categories & set(intent.categories)
        matched_tech = tool_tech & set(intent.technologies)
        matched_features = tool_features & set(intent.features)

        keyword_score, keyword_hits = self._keyword_score(tool, intent)
        pricing_score = self._pricing_score(tool, budget)

        # Only dimensions the request actually expresses count towards the
        # percentage, so an unmentioned dimension cannot cap the match at 70%.
        dimensions: list[tuple[str, float]] = []
        if intent.categories:
            dimensions.append(
                ("category", len(matched_categories) / len(intent.categories))
            )
        if intent.keywords:
            dimensions.append(("keyword", keyword_score))
        if intent.technologies:
            dimensions.append(
                ("technology", len(matched_tech) / len(intent.technologies))
            )
        if intent.features:
            dimensions.append(
                ("feature", len(matched_features) / len(intent.features))
            )
        if budget != Budget.ANY:
            dimensions.append(("pricing", pricing_score))

        if not dimensions:
            return None

        total_weight = sum(WEIGHTS[name] for name, _ in dimensions)
        raw = sum(WEIGHTS[name] * value for name, value in dimensions)
        score = round(raw / total_weight * 100)

        has_taxonomy_signal = bool(
            intent.categories or intent.technologies or intent.features
        )
        matched_taxonomy = bool(matched_categories or matched_tech or matched_features)
        # A tool must match something the user actually asked for. Being cheap
        # is not on its own a reason to recommend it.
        if not matched_taxonomy and keyword_score == 0:
            return None
        if has_taxonomy_signal and not matched_taxonomy and keyword_score < 0.5:
            return None
        if budget == Budget.FREE_ONLY and pricing_score == 0:
            return None
        if score < MIN_SCORE:
            return None

        return ScoredTool(
            tool=tool,
            score=score,
            reasons=self._reasons(
                tool, matched_categories, matched_tech, matched_features, keyword_hits
            ),
            matched_categories=sorted(matched_categories),
            matched_technologies=sorted(matched_tech),
            matched_features=sorted(matched_features),
        )

    def _reasons(
        self,
        tool: Tool,
        categories: set[str],
        technologies: set[str],
        features: set[str],
        keyword_hits: list[str],
    ) -> list[str]:
        reasons: list[str] = []
        pricing_reason = {
            PricingStatus.FREE_FOREVER: "Completely free",
            PricingStatus.OPEN_SOURCE: "Open source",
            PricingStatus.FREE_TIER: "Free tier",
            PricingStatus.FREE_CREDITS: "Free credits",
            PricingStatus.BYOK: "Free with your own API key",
            PricingStatus.FREE_TRIAL: "Free trial only",
            PricingStatus.PAID_ONLY: "Paid product",
        }.get(tool.pricing_status)
        if pricing_reason:
            reasons.append(pricing_reason)

        for name in _tag_names(tool, TagKind.TECHNOLOGY, technologies):
            reasons.append(f"{name} support")
        for name in _tag_names(tool, TagKind.FEATURE, features):
            reasons.append(name)
        for category in tool.categories:
            if category.slug in categories:
                reasons.append(category.name)

        if not categories and not technologies and not features and keyword_hits:
            reasons.append("Matches: " + ", ".join(keyword_hits[:4]))
        if tool.has_free_api:
            reasons.append("Free API access")
        if tool.has_mcp:
            reasons.append("MCP support")

        deduped: list[str] = []
        for reason in reasons:
            if reason not in deduped:
                deduped.append(reason)
        return deduped[:6]

    # -------------------------------------------------------------- pipeline

    async def rank(
        self, intent: Intent, budget: str, limit: int
    ) -> tuple[list[ScoredTool], int]:
        candidates = await self.tools.all_active()
        scored = [
            result
            for tool in candidates
            if (result := self.score_tool(tool, intent, budget)) is not None
        ]
        scored.sort(
            key=lambda item: (
                item.score,
                item.tool.featured,
                item.tool.pricing_status in FREE_PRICING_STATUSES,
                item.tool.name,
            ),
            reverse=True,
        )
        return scored[:limit], len(candidates)

    async def recommend(
        self, request: RecommendationRequest
    ) -> RecommendationResponse:
        index = await self.taxonomy()
        intent = extract_intent(request.query, index)

        # Explicit UI selections always win over inferred ones.
        for slug in request.technologies:
            if index.has(TagKind.TECHNOLOGY, slug) and slug not in intent.technologies:
                intent.technologies.append(slug)
        for slug in request.categories:
            if index.has("category", slug) and slug not in intent.categories:
                intent.categories.append(slug)

        budget = request.budget
        notes: list[str] = []
        if intent.free_intent and budget == Budget.ANY:
            budget = Budget.MOSTLY_FREE
            notes.append("Free intent detected in your wording; prioritising free tools.")
        if not intent.categories and not intent.technologies and not intent.features:
            notes.append(
                "No specific category matched, so results are ranked on keywords."
            )

        scored, considered = await self.rank(intent, budget, request.limit)
        if not scored:
            notes.append(
                "No tool passed the matching threshold. Try describing the task "
                "differently or widening your budget."
            )

        meta = RecommendationMeta(
            interpreted_keywords=intent.keywords,
            detected_categories=intent.categories,
            detected_technologies=intent.technologies,
            detected_features=intent.features,
            budget=budget,
            candidates_considered=considered,
            scoring_weights=dict(WEIGHTS),
            notes=notes,
        )
        return RecommendationResponse(
            best_match=scored[0].to_schema() if scored else None,
            other_options=[item.to_schema() for item in scored[1:]],
            meta=meta,
        )
