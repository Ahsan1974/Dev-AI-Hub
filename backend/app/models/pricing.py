from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import BillingPeriod
from app.db.base import Base, JSONColumn, TimestampMixin

if TYPE_CHECKING:
    from app.models.tool import Tool


class PricingPlan(Base, TimestampMixin):
    """One purchasable (or free) plan of a tool.

    Prices are stored as structured numbers plus a verification source so the
    dataset can be refreshed without re-parsing marketing copy.
    """

    __tablename__ = "pricing_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    tool_id: Mapped[int] = mapped_column(
        ForeignKey("tools.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    billing_period: Mapped[str] = mapped_column(
        String(20), nullable=False, default=BillingPeriod.MONTH
    )
    is_free: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_trial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    #: Per-seat plans render as "$19 / user / month".
    is_per_seat: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text)
    features: Mapped[list[str]] = mapped_column(JSONColumn, default=list)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    tool: Mapped["Tool"] = relationship(back_populates="pricing_plans")

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<PricingPlan {self.name} {self.price} {self.currency}>"
