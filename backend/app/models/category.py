from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.associations import tool_categories

if TYPE_CHECKING:
    from app.models.tool import Tool


class Category(Base, TimestampMixin):
    """A browsable grouping such as "AI Coding" or "Video Generation"."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(
        String(140), nullable=False, unique=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    #: High level grouping used for navigation ("Software Development", ...).
    group: Mapped[str] = mapped_column(String(80), nullable=False, default="General")
    icon: Mapped[str | None] = mapped_column(String(60))
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=100)

    tools: Mapped[list["Tool"]] = relationship(
        secondary=tool_categories, back_populates="categories", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Category {self.slug}>"
