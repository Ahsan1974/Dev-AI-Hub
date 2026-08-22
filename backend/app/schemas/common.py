from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    data: dict[str, str]


class ErrorBody(BaseModel):
    code: str = Field(examples=["TOOL_NOT_FOUND"])
    message: str = Field(examples=["The requested tool could not be found."])
    details: dict | None = None


class ErrorResponse(BaseModel):
    """Documented shape of every non-2xx response."""

    error: ErrorBody


class PricingStatusInfo(BaseModel):
    value: str
    label: str
    description: str
    is_free: bool


class FreeAccessLine(BaseModel):
    """One rendered bullet in the "Free access" box.

    ``ok`` renders as a check, ``warn`` as a caution sign, ``info`` as neutral.
    """

    kind: Literal["ok", "warn", "info"]
    text: str


class VerificationInfo(BaseModel):
    last_verified_at: str | None = None
    source_url: str | None = None
    note: str | None = None
    is_verified: bool = False
    is_stale: bool = False
