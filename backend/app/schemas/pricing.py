from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer

from app.core.enums import BillingPeriod
from app.schemas.common import ORMModel


class PricingPlanOut(ORMModel):
    id: int
    name: str
    price: Decimal | None = None
    currency: str = "USD"
    billing_period: str = BillingPeriod.MONTH
    is_free: bool = False
    is_trial: bool = False
    is_per_seat: bool = False
    description: str | None = None
    features: list[str] = Field(default_factory=list)

    @field_serializer("price")
    def _price(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class PricingPlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: Decimal | None = Field(default=None, ge=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    billing_period: BillingPeriod = BillingPeriod.MONTH
    is_free: bool = False
    is_trial: bool = False
    is_per_seat: bool = False
    description: str | None = None
    features: list[str] = Field(default_factory=list)
    sort_order: int = 0


class ToolPricingResponse(BaseModel):
    """Payload of ``GET /api/tools/{id}/pricing``."""

    tool_slug: str
    pricing_status: str
    pricing_summary: str | None = None
    plans: list[PricingPlanOut] = Field(default_factory=list)
    pricing_url: str | None = None
    last_verified_at: str | None = None
    verification_source_url: str | None = None
    disclaimer: str
