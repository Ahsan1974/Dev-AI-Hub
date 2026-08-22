from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.associations import collection_tools

if TYPE_CHECKING:
    from app.models.tool import Tool


class Collection(Base, TimestampMixin):
    """A curated, editorially ordered list of tools."""

    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(
        String(180), nullable=False, unique=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(60))
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    tools: Mapped[list["Tool"]] = relationship(
        secondary=collection_tools,
        back_populates="collections",
        lazy="selectin",
        order_by=collection_tools.c.position,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Collection {self.slug}>"
