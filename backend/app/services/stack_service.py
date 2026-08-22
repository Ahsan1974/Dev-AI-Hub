"""Builds a personal AI developer stack.

Each stack slot is a scoped recommendation request, so the stack inherits the
same explainable scoring as "What do I need?" instead of a second heuristic.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import Budget, TagKind
from app.schemas.recommendation import (
    StackRequest,
    StackResponse,
    StackSlot,
)
from app.services.intent import Intent, extract_intent
from app.services.recommendation_service import RecommendationService
from app.services.workflows import STACK_AREAS
from app.utils.text import slugify

BUDGET_LABELS = {
    Budget.FREE_ONLY: "free tools only",
    Budget.MOSTLY_FREE: "mostly free tools",
    Budget.ANY: "any price",
}


class StackService:
    def __init__(self, session: AsyncSession) -> None:
        self.recommendations = RecommendationService(session)

    async def build(self, request: StackRequest) -> StackResponse:
        index = await self.recommendations.taxonomy()

        context_terms = [
            request.primary_language or "",
            *request.frameworks,
            request.ide or "",
            *request.goals,
        ]
        context = extract_intent(" ".join(term for term in context_terms if term), index)

        technologies = list(context.technologies)
        integrations = list(context.integrations)
        for term in [request.primary_language, *request.frameworks, request.ide]:
            if not term:
                continue
            slug = slugify(term)
            if index.has(TagKind.TECHNOLOGY, slug) and slug not in technologies:
                technologies.append(slug)
            if index.has(TagKind.INTEGRATION, slug) and slug not in integrations:
                integrations.append(slug)

        wanted = request.include_areas or [str(area["slug"]) for area in STACK_AREAS]
        slots: list[StackSlot] = []
        unmatched: list[str] = []

        for area in STACK_AREAS:
            if str(area["slug"]) not in wanted:
                continue
            categories = [
                slug for slug in area["categories"] if index.has("category", slug)  # type: ignore[union-attr]
            ]
            intent = Intent(
                raw_query=str(area["query"]),
                keywords=extract_intent(str(area["query"]), index).keywords,
                categories=categories,
                technologies=technologies,
                features=[],
                integrations=integrations,
                free_intent=request.budget == Budget.FREE_ONLY,
            )
            scored, _ = await self.recommendations.rank(intent, request.budget, 3)
            if not scored:
                # Retry without the technology constraint before giving up.
                relaxed = Intent(
                    raw_query=intent.raw_query,
                    keywords=intent.keywords,
                    categories=categories,
                    free_intent=intent.free_intent,
                )
                scored, _ = await self.recommendations.rank(relaxed, request.budget, 3)
            if not scored:
                unmatched.append(str(area["area"]))
                continue
            slots.append(
                StackSlot(
                    area=str(area["area"]),
                    slug=str(area["slug"]),
                    description=str(area["description"]),
                    picks=[item.to_schema() for item in scored],
                )
            )

        explanation = self._explain(request, technologies, slots)
        language = request.primary_language or "your stack"
        summary = (
            f"A {BUDGET_LABELS.get(request.budget, 'balanced')} AI toolkit for "
            f"{language} covering {len(slots)} areas of the development workflow."
        )
        return StackResponse(
            slots=slots,
            summary=summary,
            explanation=explanation,
            unmatched_areas=unmatched,
        )

    def _explain(
        self, request: StackRequest, technologies: list[str], slots: list[StackSlot]
    ) -> list[str]:
        notes: list[str] = []
        if technologies:
            notes.append(
                "Tools were prioritised when they explicitly support "
                + ", ".join(technologies)
                + "."
            )
        else:
            notes.append(
                "No technology was recognised, so tools were selected on task fit only."
            )
        if request.budget == Budget.FREE_ONLY:
            notes.append(
                "Only tools with free-forever, open-source, free-tier, BYOK or "
                "free-credit access were considered. Trials were excluded."
            )
        elif request.budget == Budget.MOSTLY_FREE:
            notes.append("Free options rank first; paid tools appear only as backups.")
        if request.ide:
            notes.append(
                f"{request.ide} integrations were treated as a positive signal "
                "where the tool documents them."
            )
        if slots:
            notes.append(
                "Every pick shows its match score and the reasons behind it, so you "
                "can swap any slot for an alternative."
            )
        return notes
