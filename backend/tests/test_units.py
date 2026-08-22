"""Unit tests for the pure logic behind pricing presentation and scoring."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.enums import FreeAccessType, PricingStatus
from app.models.free_access import FreeAccessGrant
from app.models.pricing import PricingPlan
from app.models.tool import Tool
from app.seed.seeder import load_tool_data
from app.services.intent import TaxonomyIndex, extract_intent
from app.utils import presentation
from app.utils.quality import compute_quality_score
from app.utils.text import initials, keywords, slugify, tokenize, wants_free


def make_tool(**overrides) -> Tool:
    tool = Tool(
        name=overrides.pop("name", "Example"),
        slug="example",
        tagline="",
        description="",
        website_url="https://example.com",
        pricing_status=overrides.pop("pricing_status", PricingStatus.FREE_TIER),
        best_for=[],
        not_ideal_for=[],
        capabilities=[],
        categories=[],
        tags=[],
        pricing_plans=[],
        free_access_grants=[],
    )
    for key, value in overrides.items():
        setattr(tool, key, value)
    return tool


@pytest.mark.parametrize(
    "value,expected",
    [
        ("C++", "cpp"),
        ("C#", "csharp"),
        ("Node.js", "node-js"),
        ("Git & GitHub", "git-and-github"),
        ("  Spring Boot  ", "spring-boot"),
    ],
)
def test_slugify_keeps_technology_names_readable(value: str, expected: str) -> None:
    assert slugify(value) == expected


def test_tokenizer_preserves_cpp_and_csharp() -> None:
    assert "cpp" in tokenize("I write C++ daily")
    assert "csharp" in tokenize("C# and .NET")


def test_keywords_drop_filler_words() -> None:
    assert keywords("I need a tool to generate Java unit tests") == [
        "generate",
        "java",
        "unit",
        "tests",
    ]


@pytest.mark.parametrize(
    "text,expected",
    [("free java testing", True), ("open-source llm", True), ("java testing", False)],
)
def test_free_intent_detection(text: str, expected: bool) -> None:
    assert wants_free(text) is expected


def test_initials_fall_back_gracefully() -> None:
    assert initials("GitHub Copilot") == "GC"
    assert initials("Cursor") == "CU"
    assert initials("") == "?"


def test_free_access_lines_render_amounts_and_restrictions() -> None:
    tool = make_tool(
        free_access_grants=[
            FreeAccessGrant(
                type=FreeAccessType.ALLOWANCE,
                amount=100,
                unit="requests",
                period="month",
                restrictions=["Watermarked output"],
                requires_credit_card=False,
            )
        ]
    )
    lines = presentation.free_access_lines(tool)
    assert lines[0].text == "100 requests / month"
    assert ("warn", "Watermarked output") in [(l.kind, l.text) for l in lines]
    assert ("ok", "No credit card required") in [(l.kind, l.text) for l in lines]


def test_paid_only_tool_is_never_described_as_free() -> None:
    tool = make_tool(pricing_status=PricingStatus.PAID_ONLY)
    lines = presentation.free_access_lines(tool)
    assert lines[0].kind == "warn"
    assert presentation.free_access_headline(tool) == "No free tier"
    assert presentation.pricing_status_info(tool.pricing_status).is_free is False


def test_missing_free_access_data_says_so_instead_of_guessing() -> None:
    tool = make_tool()
    assert presentation.UNVERIFIED_FREE_ACCESS in presentation.free_access_headline(tool)


def test_pricing_headline_uses_the_cheapest_paid_plan() -> None:
    tool = make_tool(
        pricing_plans=[
            PricingPlan(name="Free", price=0, is_free=True, billing_period="free"),
            PricingPlan(name="Pro", price=20, billing_period="month"),
            PricingPlan(name="Team", price=40, billing_period="month", is_per_seat=True),
        ]
    )
    assert presentation.pricing_headline(tool) == "from $20 / month"


def test_pricing_headline_admits_when_it_does_not_know() -> None:
    assert presentation.pricing_headline(make_tool()) == presentation.PRICING_UNAVAILABLE


@pytest.mark.parametrize(
    "status,expected",
    [
        (PricingStatus.FREE_FOREVER, "No paid plan"),
        (PricingStatus.OPEN_SOURCE, "Free to self-host"),
        (PricingStatus.BYOK, "You pay your model provider"),
    ],
)
def test_tools_without_a_paid_tier_are_not_called_unpriced(
    status: PricingStatus, expected: str
) -> None:
    assert presentation.pricing_headline(make_tool(pricing_status=status)) == expected


def test_verified_label_reads_as_a_month() -> None:
    tool = make_tool(last_verified_at=datetime(2026, 8, 1, tzinfo=timezone.utc))
    assert presentation.verified_label(tool) == "August 2026"
    assert presentation.verified_label(make_tool()) is None


def test_verification_flags_stale_records() -> None:
    fresh = make_tool(last_verified_at=datetime.now(timezone.utc))
    stale = make_tool(last_verified_at=datetime.now(timezone.utc) - timedelta(days=400))
    assert presentation.verification_info(fresh).is_stale is False
    assert presentation.verification_info(stale).is_stale is True
    assert presentation.verification_info(make_tool()).is_verified is False


def test_quality_score_is_bounded_and_itemised() -> None:
    score = compute_quality_score(make_tool())
    assert 0 <= score.score <= 100
    assert sum(component.max_score for component in score.components) == 100


def test_intent_extraction_maps_phrasing_to_taxonomy() -> None:
    class FakeIndex(TaxonomyIndex):
        def __init__(self) -> None:  # skip the DB-backed constructor
            self.category_slugs = {"testing", "ai-coding"}
            self.tag_slugs = {"technology": {"java"}, "feature": {"testing"}}
            self._words = {"java": {("technology", "java")}}

    intent = extract_intent("free tool to write unit tests in Java", FakeIndex())
    assert "testing" in intent.categories
    assert "java" in intent.technologies
    assert intent.free_intent is True


def test_seed_dataset_meets_the_mvp_bar() -> None:
    tools = load_tool_data()
    assert len(tools) >= 500

    slugs = [tool.get("slug") or slugify(tool["name"]) for tool in tools]
    assert len(slugs) == len(set(slugs)), "duplicate slugs in the seed dataset"

    free = [
        tool
        for tool in tools
        if tool["pricing_status"]
        in {"FREE_FOREVER", "FREE_TIER", "FREE_CREDITS", "OPEN_SOURCE", "BYOK"}
    ]
    assert len(free) / len(tools) > 0.5, "most seeded tools should have free access"

    for tool in tools:
        assert tool["website_url"].startswith("https://"), tool["name"]
        assert tool["description"], tool["name"]
        assert tool["categories"], tool["name"]
        priced = [
            plan for plan in tool.get("pricing_plans", []) if plan.get("price")
        ]
        if priced:
            assert tool.get("verification_source_url"), (
                f"{tool['name']} states prices without a verification source"
            )


def test_every_seeded_category_slug_exists() -> None:
    import json
    from pathlib import Path

    from app.seed.seeder import DATA_DIR

    known = {
        item["slug"]
        for item in json.loads((DATA_DIR / "categories.json").read_text("utf-8"))
    }
    for tool in load_tool_data():
        unknown = set(tool["categories"]) - known
        assert not unknown, f"{tool['name']} references unknown categories {unknown}"
