"""Turn stored data into the exact statements the UI shows.

Rendering lives here (not in components) so the API, comparison table and future
exports all describe pricing and free access identically.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.core.enums import (
    FREE_PRICING_STATUSES,
    PRICING_STATUS_DESCRIPTIONS,
    PRICING_STATUS_LABELS,
    FreeAccessType,
    PricingStatus,
)
from app.models.free_access import FreeAccessGrant
from app.models.tool import Tool
from app.schemas.common import FreeAccessLine, PricingStatusInfo, VerificationInfo

#: Data older than this is flagged in the UI as worth re-checking.
STALE_AFTER = timedelta(days=180)

PRICING_UNAVAILABLE = (
    "Pricing information unavailable. Check the provider's official pricing page."
)

UNVERIFIED_FREE_ACCESS = (
    "Free tier available. Current limits should be checked on the "
    "provider's pricing page."
)


def pricing_status_info(status: str) -> PricingStatusInfo:
    return PricingStatusInfo(
        value=status,
        label=PRICING_STATUS_LABELS.get(status, status.replace("_", " ").title()),
        description=PRICING_STATUS_DESCRIPTIONS.get(status, ""),
        is_free=status in FREE_PRICING_STATUSES,
    )


def _format_amount(amount: Decimal | float | None) -> str:
    if amount is None:
        return ""
    value = float(amount)
    if value >= 1000 and value == int(value):
        return f"{int(value):,}"
    return str(int(value)) if value == int(value) else f"{value:g}"


def grant_headline(grant: FreeAccessGrant) -> str:
    """"100 requests / month" or the free-form description when no number exists."""
    if grant.amount is not None and grant.unit:
        text = f"{_format_amount(grant.amount)} {grant.unit}"
        if grant.period:
            text += f" / {grant.period}"
        return text
    if grant.description:
        return grant.description
    if grant.type == FreeAccessType.SELF_HOST:
        return "Open source and self-hostable"
    if grant.type == FreeAccessType.BYOK:
        return "Free to use with your own API key"
    if grant.type == FreeAccessType.UNLIMITED:
        return "Unlimited free usage"
    return UNVERIFIED_FREE_ACCESS


def free_access_lines(tool: Tool) -> list[FreeAccessLine]:
    """Bullets for the "Free access" box, in display order."""
    lines: list[FreeAccessLine] = []

    if tool.pricing_status == PricingStatus.PAID_ONLY and not tool.free_access_grants:
        lines.append(
            FreeAccessLine(kind="warn", text="No meaningful free tier available.")
        )
        if tool.free_access_summary:
            lines.append(FreeAccessLine(kind="info", text=tool.free_access_summary))
        return lines

    for grant in tool.free_access_grants:
        headline = grant_headline(grant)
        lines.append(FreeAccessLine(kind="ok", text=headline))
        if grant.description and grant.description != headline:
            lines.append(FreeAccessLine(kind="info", text=grant.description))
        for restriction in grant.restrictions or []:
            lines.append(FreeAccessLine(kind="warn", text=restriction))
        if grant.requires_credit_card is True:
            lines.append(FreeAccessLine(kind="warn", text="Credit card required"))
        elif grant.requires_credit_card is False:
            lines.append(FreeAccessLine(kind="ok", text="No credit card required"))
        if grant.expires:
            text = "Free access expires"
            if grant.expires_after_days:
                text = f"Expires after {grant.expires_after_days} days"
            lines.append(FreeAccessLine(kind="warn", text=text))

    if not lines:
        lines.append(
            FreeAccessLine(
                kind="info",
                text=tool.free_access_summary or UNVERIFIED_FREE_ACCESS,
            )
        )
    return lines


def free_access_headline(tool: Tool) -> str:
    """One-line free summary for cards and comparison cells."""
    if tool.free_access_summary:
        return tool.free_access_summary
    if tool.pricing_status == PricingStatus.PAID_ONLY:
        return "No free tier"
    if tool.free_access_grants:
        return grant_headline(tool.free_access_grants[0])
    return UNVERIFIED_FREE_ACCESS


def requires_credit_card(tool: Tool) -> bool | None:
    values = [
        grant.requires_credit_card
        for grant in tool.free_access_grants
        if grant.requires_credit_card is not None
    ]
    if not values:
        return None
    return any(values)


def free_access_expires(tool: Tool) -> bool | None:
    if tool.pricing_status == PricingStatus.FREE_TRIAL:
        return True
    values = [g.expires for g in tool.free_access_grants if g.expires is not None]
    if not values:
        return None
    return all(values)


def pricing_headline(tool: Tool) -> str:
    """Cheapest non-free plan rendered as "from $20 / month"."""
    paid = [
        plan
        for plan in tool.pricing_plans
        if not plan.is_free and plan.price is not None and float(plan.price) > 0
    ]
    if not paid:
        if tool.pricing_summary:
            return tool.pricing_summary
        # "Unavailable" would be misleading for tools that have no paid tier at
        # all, so say what is actually true of each pricing model.
        if tool.pricing_status == PricingStatus.FREE_FOREVER:
            return "No paid plan"
        if tool.pricing_status == PricingStatus.OPEN_SOURCE:
            return "Free to self-host"
        if tool.pricing_status == PricingStatus.BYOK:
            return "You pay your model provider"
        return PRICING_UNAVAILABLE
    cheapest = min(paid, key=lambda plan: float(plan.price or 0))
    price = float(cheapest.price or 0)
    amount = f"{price:.0f}" if price == int(price) else f"{price:.2f}"
    currency = cheapest.currency or "USD"
    symbol = "$" if currency == "USD" else f"{currency} "
    suffix = (
        "/ user / month"
        if cheapest.is_per_seat
        else f"/ {cheapest.billing_period or 'month'}"
    )
    return f"from {symbol}{amount} {suffix}"


def verified_label(tool: Tool) -> str | None:
    """Human month-and-year wording, e.g. ``August 2026``."""
    if tool.last_verified_at is None:
        return None
    return tool.last_verified_at.strftime("%B %Y")


def verification_info(tool: Tool) -> VerificationInfo:
    verified_at = tool.last_verified_at
    is_stale = False
    if verified_at is not None:
        reference = verified_at
        if reference.tzinfo is None:
            reference = reference.replace(tzinfo=timezone.utc)
        is_stale = datetime.now(timezone.utc) - reference > STALE_AFTER
    return VerificationInfo(
        last_verified_at=verified_at.isoformat() if verified_at else None,
        source_url=tool.verification_source_url,
        note=tool.verification_note,
        is_verified=verified_at is not None,
        is_stale=is_stale,
    )
