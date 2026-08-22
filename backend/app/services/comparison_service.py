"""Side-by-side comparison.

Unknown values are rendered as "unknown" rather than a cross, so a data gap is
never presented as a missing feature.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import TagKind
from app.core.errors import ValidationError
from app.models.tool import Tool
from app.repositories.tool_repository import ToolRepository
from app.schemas.compare import (
    MAX_COMPARE_TOOLS,
    CompareCell,
    CompareRequest,
    CompareResponse,
    CompareRow,
)
from app.schemas.tool import ToolDetail
from app.utils import presentation

_BOOL_ROWS: tuple[tuple[str, str, str], ...] = (
    ("is_open_source", "Open source", "Capabilities"),
    ("has_api", "API", "Capabilities"),
    ("has_free_api", "Free API tier", "Capabilities"),
    ("has_agent", "Agent mode", "Capabilities"),
    ("has_mcp", "MCP support", "Capabilities"),
    ("has_local_model", "Local models", "Capabilities"),
    ("self_hostable", "Self-hostable", "Capabilities"),
)


def _tag_names(tool: Tool, kind: str) -> list[str]:
    return [tag.name for tag in tool.tags if tag.kind == kind]


class ComparisonService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ToolRepository(session)

    async def compare(self, request: CompareRequest) -> CompareResponse:
        if len(request.slugs) > MAX_COMPARE_TOOLS:
            raise ValidationError(
                f"You can compare at most {MAX_COMPARE_TOOLS} tools at once.",
                code="TOO_MANY_TOOLS",
            )
        found = await self.repo.get_many_by_slugs(request.slugs)
        by_slug = {tool.slug: tool for tool in found}
        tools = [by_slug[slug] for slug in request.slugs if slug in by_slug]
        missing = [slug for slug in request.slugs if slug not in by_slug]

        if len(tools) < 2:
            raise ValidationError(
                "At least two of the requested tools must exist to compare them.",
                code="COMPARE_NOT_ENOUGH_TOOLS",
                details={"missing_slugs": missing},
            )

        return CompareResponse(
            tools=[ToolDetail.from_model(tool) for tool in tools],
            rows=self._rows(tools),
            missing_slugs=missing,
        )

    def _rows(self, tools: list[Tool]) -> list[CompareRow]:
        rows: list[CompareRow] = [
            CompareRow(
                key="pricing_status",
                label="Free status",
                group="Pricing",
                cells=[
                    CompareCell(
                        kind="text",
                        value=presentation.pricing_status_info(tool.pricing_status).label,
                    )
                    for tool in tools
                ],
            ),
            CompareRow(
                key="free_allowance",
                label="Free allowance",
                group="Pricing",
                cells=[
                    CompareCell(
                        kind="text", value=presentation.free_access_headline(tool)
                    )
                    for tool in tools
                ],
            ),
            CompareRow(
                key="paid_pricing",
                label="Paid pricing",
                group="Pricing",
                cells=[
                    CompareCell(kind="price", value=presentation.pricing_headline(tool))
                    for tool in tools
                ],
            ),
            CompareRow(
                key="requires_credit_card",
                label="Credit card for free tier",
                group="Pricing",
                cells=[
                    self._tri_state(presentation.requires_credit_card(tool))
                    for tool in tools
                ],
            ),
            CompareRow(
                key="free_expires",
                label="Free access expires",
                group="Pricing",
                cells=[
                    self._tri_state(presentation.free_access_expires(tool))
                    for tool in tools
                ],
            ),
        ]

        rows += [
            CompareRow(
                key=attribute,
                label=label,
                group=group,
                cells=[
                    CompareCell(kind="bool", value=bool(getattr(tool, attribute)))
                    for tool in tools
                ],
            )
            for attribute, label, group in _BOOL_ROWS
        ]

        rows += [
            CompareRow(
                key="languages",
                label="Languages",
                group="Developer support",
                cells=[
                    self._list_cell(_tag_names(tool, TagKind.TECHNOLOGY))
                    for tool in tools
                ],
            ),
            CompareRow(
                key="platforms",
                label="Platforms",
                group="Developer support",
                cells=[
                    self._list_cell(_tag_names(tool, TagKind.PLATFORM))
                    for tool in tools
                ],
            ),
            CompareRow(
                key="integrations",
                label="Integrations",
                group="Developer support",
                cells=[
                    self._list_cell(_tag_names(tool, TagKind.INTEGRATION))
                    for tool in tools
                ],
            ),
            CompareRow(
                key="categories",
                label="Categories",
                group="Developer support",
                cells=[
                    self._list_cell([c.name for c in tool.categories]) for tool in tools
                ],
            ),
            CompareRow(
                key="best_for",
                label="Best for",
                group="Fit",
                cells=[self._list_cell(tool.best_for or []) for tool in tools],
            ),
            CompareRow(
                key="not_ideal_for",
                label="Not ideal for",
                group="Fit",
                cells=[self._list_cell(tool.not_ideal_for or []) for tool in tools],
            ),
            CompareRow(
                key="verified",
                label="Last verified",
                group="Data",
                cells=[
                    CompareCell(
                        kind="text",
                        value=presentation.verified_label(tool),
                        note=None if tool.last_verified_at else "Not verified yet",
                    )
                    for tool in tools
                ],
            ),
        ]
        return rows

    @staticmethod
    def _tri_state(value: bool | None) -> CompareCell:
        if value is None:
            return CompareCell(kind="unknown", value=None, note="Not documented")
        return CompareCell(kind="bool", value=value)

    @staticmethod
    def _list_cell(values: list[str]) -> CompareCell:
        if not values:
            return CompareCell(kind="unknown", value=[], note="Not documented")
        return CompareCell(kind="list", value=values)
