from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.core.enums import PricingStatus, TagKind
from app.models.tool import Tool
from app.schemas.category import CategoryOut
from app.schemas.common import FreeAccessLine, ORMModel, PricingStatusInfo, VerificationInfo
from app.schemas.free_access import FreeAccessGrantCreate, FreeAccessGrantOut
from app.schemas.pricing import PricingPlanCreate, PricingPlanOut
from app.schemas.tag import TagOut
from app.utils import presentation
from app.utils.quality import QualityScore, compute_quality_score
from app.utils.text import initials


class ToolCapabilities(BaseModel):
    is_open_source: bool = False
    has_api: bool = False
    has_free_api: bool = False
    has_mcp: bool = False
    has_agent: bool = False
    has_local_model: bool = False
    self_hostable: bool = False


def _tag_names(tool: Tool, kind: str) -> list[str]:
    return [tag.name for tag in tool.tags if tag.kind == kind]


class ToolSummary(ORMModel):
    """Shape consumed by `ToolCard` and every list surface."""

    id: int
    name: str
    slug: str
    tagline: str
    description: str
    website_url: str
    logo_url: str | None = None
    initials: str = ""

    pricing_status: str
    pricing: PricingStatusInfo
    pricing_headline: str
    free_access_headline: str
    free_access_lines: list[FreeAccessLine] = Field(default_factory=list)

    categories: list[CategoryOut] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)

    flags: ToolCapabilities
    featured: bool = False
    is_verified: bool = False
    last_verified_at: datetime | None = None
    created_at: datetime | None = None

    @classmethod
    def from_model(cls, tool: Tool) -> "ToolSummary":
        return cls(
            id=tool.id,
            name=tool.name,
            slug=tool.slug,
            tagline=tool.tagline,
            description=tool.description,
            website_url=tool.website_url,
            logo_url=tool.logo_url,
            initials=initials(tool.name),
            pricing_status=tool.pricing_status,
            pricing=presentation.pricing_status_info(tool.pricing_status),
            pricing_headline=presentation.pricing_headline(tool),
            free_access_headline=presentation.free_access_headline(tool),
            free_access_lines=presentation.free_access_lines(tool)[:3],
            categories=[CategoryOut.model_validate(c) for c in tool.categories],
            languages=_tag_names(tool, TagKind.TECHNOLOGY),
            features=_tag_names(tool, TagKind.FEATURE),
            platforms=_tag_names(tool, TagKind.PLATFORM),
            integrations=_tag_names(tool, TagKind.INTEGRATION),
            flags=ToolCapabilities.model_validate(tool, from_attributes=True),
            featured=tool.featured,
            is_verified=tool.last_verified_at is not None,
            last_verified_at=tool.last_verified_at,
            created_at=tool.created_at,
        )


class ToolDetail(ToolSummary):
    long_description: str | None = None
    pricing_url: str | None = None
    docs_url: str | None = None
    repo_url: str | None = None

    pricing_summary: str | None = None
    free_access_summary: str | None = None
    free_access_grants: list[FreeAccessGrantOut] = Field(default_factory=list)
    pricing_plans: list[PricingPlanOut] = Field(default_factory=list)

    capabilities: list[str] = Field(default_factory=list)
    best_for: list[str] = Field(default_factory=list)
    not_ideal_for: list[str] = Field(default_factory=list)
    tags: list[TagOut] = Field(default_factory=list)

    requires_credit_card: bool | None = None
    free_access_expires: bool | None = None

    verification: VerificationInfo
    quality: QualityScore
    updated_at: datetime | None = None

    @classmethod
    def from_model(cls, tool: Tool) -> "ToolDetail":
        base = ToolSummary.from_model(tool).model_dump()
        base.update(
            free_access_lines=presentation.free_access_lines(tool),
            long_description=tool.long_description,
            pricing_url=tool.pricing_url,
            docs_url=tool.docs_url,
            repo_url=tool.repo_url,
            pricing_summary=tool.pricing_summary or presentation.PRICING_UNAVAILABLE,
            free_access_summary=tool.free_access_summary,
            free_access_grants=[
                FreeAccessGrantOut.model_validate(g) for g in tool.free_access_grants
            ],
            pricing_plans=[
                PricingPlanOut.model_validate(p) for p in tool.pricing_plans
            ],
            capabilities=tool.capabilities or [],
            best_for=tool.best_for or [],
            not_ideal_for=tool.not_ideal_for or [],
            tags=[TagOut.model_validate(t) for t in tool.tags],
            requires_credit_card=presentation.requires_credit_card(tool),
            free_access_expires=presentation.free_access_expires(tool),
            verification=presentation.verification_info(tool),
            quality=compute_quality_score(tool),
            updated_at=tool.updated_at,
        )
        return cls.model_validate(base)


class ToolWithScore(BaseModel):
    """A tool plus the explained score produced by the recommender."""

    tool: ToolSummary
    score: int = Field(ge=0, le=100)
    reasons: list[str] = Field(default_factory=list)
    matched_categories: list[str] = Field(default_factory=list)
    matched_technologies: list[str] = Field(default_factory=list)
    matched_features: list[str] = Field(default_factory=list)


class ToolWrite(BaseModel):
    """Admin payload for creating or replacing a tool."""

    name: str = Field(min_length=1, max_length=160)
    slug: str | None = Field(default=None, max_length=180)
    tagline: str = Field(default="", max_length=160)
    description: str = ""
    long_description: str | None = None

    website_url: HttpUrl
    pricing_url: HttpUrl | None = None
    docs_url: HttpUrl | None = None
    repo_url: HttpUrl | None = None
    logo_url: HttpUrl | None = None

    pricing_status: PricingStatus = PricingStatus.PAID_ONLY
    free_access_summary: str | None = None
    pricing_summary: str | None = None

    best_for: list[str] = Field(default_factory=list)
    not_ideal_for: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)

    is_open_source: bool = False
    has_api: bool = False
    has_free_api: bool = False
    has_mcp: bool = False
    has_agent: bool = False
    has_local_model: bool = False
    self_hostable: bool = False

    featured: bool = False
    is_active: bool = True

    last_verified_at: datetime | None = None
    verification_source_url: HttpUrl | None = None
    verification_note: str | None = None

    categories: list[str] = Field(default_factory=list, description="Category slugs")
    technologies: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)

    pricing_plans: list[PricingPlanCreate] = Field(default_factory=list)
    free_access: list[FreeAccessGrantCreate] = Field(default_factory=list)

    @field_validator("website_url", "pricing_url", "docs_url", "repo_url", "logo_url")
    @classmethod
    def _https_only(cls, value: HttpUrl | None) -> HttpUrl | None:
        if value is not None and value.scheme not in {"http", "https"}:
            raise ValueError("Only http(s) URLs are allowed.")
        return value


class ToolPatch(BaseModel):
    """Admin payload for partial updates. Unset fields stay untouched."""

    model_config = {"extra": "forbid"}

    name: str | None = Field(default=None, min_length=1, max_length=160)
    tagline: str | None = None
    description: str | None = None
    long_description: str | None = None
    website_url: HttpUrl | None = None
    pricing_url: HttpUrl | None = None
    docs_url: HttpUrl | None = None
    repo_url: HttpUrl | None = None
    logo_url: HttpUrl | None = None
    pricing_status: PricingStatus | None = None
    free_access_summary: str | None = None
    pricing_summary: str | None = None
    best_for: list[str] | None = None
    not_ideal_for: list[str] | None = None
    capabilities: list[str] | None = None
    is_open_source: bool | None = None
    has_api: bool | None = None
    has_free_api: bool | None = None
    has_mcp: bool | None = None
    has_agent: bool | None = None
    has_local_model: bool | None = None
    self_hostable: bool | None = None
    featured: bool | None = None
    is_active: bool | None = None
    last_verified_at: datetime | None = None
    verification_source_url: HttpUrl | None = None
    verification_note: str | None = None
    categories: list[str] | None = None
    technologies: list[str] | None = None
    features: list[str] | None = None
    platforms: list[str] | None = None
    integrations: list[str] | None = None
    pricing_plans: list[PricingPlanCreate] | None = None
    free_access: list[FreeAccessGrantCreate] | None = None

    def changes(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)
