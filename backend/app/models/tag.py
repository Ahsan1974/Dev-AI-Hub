from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import TagKind
from app.db.base import Base, TimestampMixin
from app.models.associations import tool_tags

if TYPE_CHECKING:
    from app.models.tool import Tool


class Tag(Base, TimestampMixin):
    """Technology, feature, platform or integration marker attached to tools."""

    __tablename__ = "tags"
    __table_args__ = (
        Index("ix_tags_kind_slug", "kind", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(
        String(30), nullable=False, default=TagKind.TECHNOLOGY, index=True
    )

    tools: Mapped[list["Tool"]] = relationship(
        secondary=tool_tags, back_populates="tags", lazy="selectin"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<Tag {self.kind}:{self.slug}>"
