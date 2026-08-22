from __future__ import annotations

from httpx import AsyncClient

from app.core.enums import FREE_PRICING_STATUSES

JAVA_TESTS = "I need a free AI tool to generate Java unit tests"


async def test_recommendations_explain_every_match(client: AsyncClient) -> None:
    response = await client.post(
        "/api/recommendations", json={"query": JAVA_TESTS, "budget": "free_only"}
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    best = payload["best_match"]
    assert best is not None
    assert 0 < best["score"] <= 100
    assert best["reasons"]
    assert "java" in best["matched_technologies"]
    assert "testing" in best["matched_categories"]
    assert payload["meta"]["scoring_weights"]["category"] == 30


async def test_java_testing_query_surfaces_java_testing_tools(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/recommendations",
        json={"query": JAVA_TESTS, "budget": "free_only", "limit": 5},
    )
    payload = response.json()["data"]
    slugs = [payload["best_match"]["tool"]["slug"]] + [
        item["tool"]["slug"] for item in payload["other_options"]
    ]
    assert {"qodo", "diffblue-cover"} & set(slugs)


async def test_free_only_budget_excludes_paid_and_trial_tools(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/recommendations",
        json={"query": "generate images from text", "budget": "free_only", "limit": 10},
    )
    payload = response.json()["data"]
    results = [payload["best_match"], *payload["other_options"]]
    statuses = {item["tool"]["pricing_status"] for item in results if item}
    assert statuses <= set(FREE_PRICING_STATUSES)
    assert "PAID_ONLY" not in statuses


async def test_any_budget_can_include_paid_tools(client: AsyncClient) -> None:
    response = await client.post(
        "/api/recommendations",
        json={"query": "high quality image generation", "budget": "any", "limit": 12},
    )
    payload = response.json()["data"]
    results = [payload["best_match"], *payload["other_options"]]
    assert any(item["tool"]["pricing_status"] == "PAID_ONLY" for item in results)


async def test_detected_intent_is_reported_back(client: AsyncClient) -> None:
    response = await client.post(
        "/api/recommendations",
        json={"query": "debug my kubernetes cluster", "budget": "mostly_free"},
    )
    meta = response.json()["data"]["meta"]
    assert "debugging" in meta["detected_categories"]
    assert "kubernetes" in meta["detected_technologies"]
    assert meta["candidates_considered"] > 0


async def test_nonsense_query_returns_no_best_match_with_a_reason(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/recommendations",
        json={"query": "qqqq zzzz vvvv wwww", "budget": "free_only"},
    )
    payload = response.json()["data"]
    assert payload["best_match"] is None
    assert payload["meta"]["notes"]


async def test_short_query_is_rejected(client: AsyncClient) -> None:
    response = await client.post("/api/recommendations", json={"query": "a"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_ai_endpoint_falls_back_without_a_provider(client: AsyncClient) -> None:
    response = await client.post(
        "/api/recommendations/ai", json={"query": JAVA_TESTS, "budget": "free_only"}
    )
    assert response.status_code == 200
    meta = response.json()["data"]["meta"]
    assert meta["strategy"] == "rule_based_scoring"
    assert any("No LLM provider" in note for note in meta["notes"])


async def test_stack_builder_returns_explained_slots(client: AsyncClient) -> None:
    response = await client.post(
        "/api/recommendations/stack",
        json={
            "primary_language": "Java",
            "frameworks": ["Spring Boot"],
            "ide": "IntelliJ IDEA",
            "goals": ["developer productivity"],
            "budget": "free_only",
        },
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["slots"]
    assert payload["explanation"]
    areas = {slot["area"] for slot in payload["slots"]}
    assert {"Coding", "Testing"} <= areas
    for slot in payload["slots"]:
        assert slot["picks"]
        for pick in slot["picks"]:
            assert pick["tool"]["pricing_status"] in FREE_PRICING_STATUSES
