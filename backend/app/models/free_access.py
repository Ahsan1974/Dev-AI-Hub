from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import FreeAccessType
from app.db.base import Base, JSONColumn, TimestampMixin

if TYPE_CHECKING:
    from app.models.tool import Tool


class FreeAccessGrant(Base, TimestampMixin):
    """A single structured statement about what a tool gives away for free.

    A tool can own several grants, e.g. "20 image generations / month" plus
    "unlimited community models". Amounts stay nullable because many providers
    publish qualitative limits only - we never invent numbers.
    """

    __tablename__ = "free_access_grants"

    id: Mapped[int] = mapped_column(primary_key=True)
    tool_id: Mapped[int] = mapped_column(
        ForeignKey("tools.id", ondelete="CASCADE"), nullable=False, index=True
    )

    type: Mapped[str] = mapped_column(
        String(30), nullable=False, default=FreeAccessType.UNKNOWN
    )
    amount: Mapped[float | None] = mapped_column(Numeric(12, 2))
    unit: Mapped[str | None] = mapped_column(String(30))
    period: Mapped[str | None] = mapped_column(String(30))
    description: Mapped[str | None] = mapped_column(Text)
    restrictions: Mapped[list[str]] = mapped_column(JSONColumn, default=list)
    requires_credit_card: Mapped[bool | None] = mapped_column(Boolean)
    expires: Mapped[bool | None] = mapped_column(Boolean)
    expires_after_days: Mapped[int | None] = mapped_column(Integer)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    tool: Mapped["Tool"] = relationship(back_populates="free_access_grants")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<FreeAccessGrant {self.type} {self.amount} {self.unit}>"
