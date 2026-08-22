"""Domain enumerations shared by models, schemas and services."""

from __future__ import annotations

from enum import StrEnum


class PricingStatus(StrEnum):
    """Standardised pricing state of a tool.

    The distinction matters: a 30 day trial must never be presented as "Free".
    """

    FREE_FOREVER = "FREE_FOREVER"
    FREE_TIER = "FREE_TIER"
    FREE_CREDITS = "FREE_CREDITS"
    FREE_TRIAL = "FREE_TRIAL"
    OPEN_SOURCE = "OPEN_SOURCE"
    BYOK = "BYOK"
    PAID_ONLY = "PAID_ONLY"


PRICING_STATUS_LABELS: dict[str, str] = {
    PricingStatus.FREE_FOREVER: "Free forever",
    PricingStatus.FREE_TIER: "Free tier",
    PricingStatus.FREE_CREDITS: "Free credits",
    PricingStatus.FREE_TRIAL: "Free trial",
    PricingStatus.OPEN_SOURCE: "Open source",
    PricingStatus.BYOK: "Bring your own key",
    PricingStatus.PAID_ONLY: "Paid only",
}

PRICING_STATUS_DESCRIPTIONS: dict[str, str] = {
    PricingStatus.FREE_FOREVER: "The free offering does not expire.",
    PricingStatus.FREE_TIER: "A recurring, limited free tier is available.",
    PricingStatus.FREE_CREDITS: "A limited amount of one-off or recurring credits.",
    PricingStatus.FREE_TRIAL: "Temporary access to paid functionality only.",
    PricingStatus.OPEN_SOURCE: (
        "The software is open source; hosting, API or model costs may still apply."
    ),
    PricingStatus.BYOK: "Free to use, but you supply your own model API key.",
    PricingStatus.PAID_ONLY: "No meaningful free tier.",
}

#: Statuses that qualify a tool for the "free tools" surfaces of the product.
FREE_PRICING_STATUSES: tuple[str, ...] = (
    PricingStatus.FREE_FOREVER,
    PricingStatus.FREE_TIER,
    PricingStatus.FREE_CREDITS,
    PricingStatus.OPEN_SOURCE,
    PricingStatus.BYOK,
)

#: Ranking weight used when sorting "most free first".
PRICING_FREENESS_RANK: dict[str, int] = {
    PricingStatus.FREE_FOREVER: 6,
    PricingStatus.OPEN_SOURCE: 5,
    PricingStatus.FREE_TIER: 4,
    PricingStatus.BYOK: 3,
    PricingStatus.FREE_CREDITS: 2,
    PricingStatus.FREE_TRIAL: 1,
    PricingStatus.PAID_ONLY: 0,
}


class FreeAccessType(StrEnum):
    ALLOWANCE = "ALLOWANCE"
    CREDITS = "CREDITS"
    TRIAL = "TRIAL"
    SELF_HOST = "SELF_HOST"
    BYOK = "BYOK"
    UNLIMITED = "UNLIMITED"
    UNKNOWN = "UNKNOWN"


class FreeAccessUnit(StrEnum):
    REQUESTS = "requests"
    CREDITS = "credits"
    GENERATIONS = "generations"
    MINUTES = "minutes"
    TOKENS = "tokens"
    IMAGES = "images"
    VIDEOS = "videos"
    HOURS = "hours"
    MESSAGES = "messages"
    COMPLETIONS = "completions"
    PROJECTS = "projects"
    SEATS = "seats"
    CHARACTERS = "characters"


class BillingPeriod(StrEnum):
    MONTH = "month"
    YEAR = "year"
    ONE_TIME = "one_time"
    USAGE = "usage"
    FREE = "free"


class TagKind(StrEnum):
    TECHNOLOGY = "technology"
    FEATURE = "feature"
    PLATFORM = "platform"
    INTEGRATION = "integration"


class Budget(StrEnum):
    FREE_ONLY = "free_only"
    MOSTLY_FREE = "mostly_free"
    ANY = "any"
