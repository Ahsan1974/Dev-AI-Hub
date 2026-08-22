from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import PricingStatus
from app.db.base import Base, JSONColumn, TimestampMixin, UTCDateTime
from app.models.associations import collection_tools, tool_categories, tool_tags

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.collection import Collection
    from app.models.free_access import FreeAccessGrant
    from app.models.pricing import PricingPlan
    from app.models.tag import Tag


class Tool(Base, TimestampMixin):
    """An AI tool listed on the platform."""

    __tablename__ = "tools"
    __table_args__ = (
        Index("ix_tools_featured_pricing", "featured", "pricing_status"),
        Index("ix_tools_active_created", "is_active", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(
        String(180), nullable=False, unique=True, index=True
    )
    #: Short label under the name, e.g. "AI Code Editor".
    tagline: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    long_description: Mapped[str | None] = mapped_column(Text)

    website_url: Mapped[str] = mapped_column(String(500), nullable=False)
    pricing_url: Mapped[str | None] = mapped_column(String(500))
    docs_url: Mapped[str | None] = mapped_column(String(500))
    repo_url: Mapped[str | None] = mapped_column(String(500))
    logo_url: Mapped[str | None] = mapped_column(String(500))

    pricing_status: Mapped[str] = mapped_column(
        String(30), nullable=False, default=PricingStatus.PAID_ONLY, index=True
    )
    free_access_summary: Mapped[str | None] = mapped_column(Text)
    pricing_summary: Mapped[str | None] = mapped_column(Text)

    best_for: Mapped[list[str]] = mapped_column(JSONColumn, default=list)
    not_ideal_for: Mapped[list[str]] = mapped_column(JSONColumn, default=list)
    capabilities: Mapped[list[str]] = mapped_column(JSONColumn, default=list)

    is_open_source: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_api: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_free_api: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_mcp: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_agent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_local_model: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_hostable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    last_verified_at: Mapped[datetime | None] = mapped_column(UTCDateTime, index=True)
    verification_source_url: Mapped[str | None] = mapped_column(String(500))
    verification_note: Mapped[str | None] = mapped_column(Text)

    #: Denormalised haystack (name, tagline, description, categories, tags,
    #: best-for, free access). Rebuilt on write; indexed with GIN on PostgreSQL.
    search_text: Mapped[str] = mapped_column(Text, nullable=False, default="")

    categories: Mapped[list["Category"]] = relationship(
        secondary=tool_categories,
        back_populates="tools",
        lazy="selectin",
        order_by="Category.sort_order",
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary=tool_tags, back_populates="tools", lazy="selectin", order_by="Tag.name"
    )
    pricing_plans: Mapped[list["PricingPlan"]] = relationship(
        back_populates="tool",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="PricingPlan.sort_order",
    )
    free_access_grants: Mapped[list["FreeAccessGrant"]] = relationship(
        back_populates="tool",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="FreeAccessGrant.sort_order",
    )
    collections: Mapped[list["Collection"]] = relationship(
        secondary=collection_tools, back_populates="tools", lazy="noload"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Tool {self.slug}>"
