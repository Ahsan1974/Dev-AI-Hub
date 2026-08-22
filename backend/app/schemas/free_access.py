from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer

from app.core.enums import FreeAccessType
from app.schemas.common import ORMModel


class FreeAccessGrantOut(ORMModel):
    id: int
    type: str
    amount: Decimal | None = None
    unit: str | None = None
    period: str | None = None
    description: str | None = None
    restrictions: list[str] = Field(default_factory=list)
    requires_credit_card: bool | None = None
    expires: bool | None = None
    expires_after_days: int | None = None

    @field_serializer("amount")
    def _amount(self, value: Decimal | None) -> float | None:
        return float(value) if value is not None else None


class FreeAccessGrantCreate(BaseModel):
    type: FreeAccessType = FreeAccessType.UNKNOWN
    amount: float | None = Field(default=None, ge=0)
    unit: str | None = None
    period: str | None = None
    description: str | None = None
    restrictions: list[str] = Field(default_factory=list)
    requires_credit_card: bool | None = None
    expires: bool | None = None
    expires_after_days: int | None = Field(default=None, ge=0)
    sort_order: int = 0
