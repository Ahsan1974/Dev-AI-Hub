from __future__ import annotations

from httpx import AsyncClient

from app.core.enums import FREE_PRICING_STATUSES


async def test_search_finds_tools_by_name(client: AsyncClient) -> None:
    response = await client.get("/api/search", params={"q": "cursor"})
    assert response.status_code == 200
    body = response.json()
    assert body["data"][0]["slug"] == "cursor"
    assert body["meta"]["query"] == "cursor"
    assert body["meta"]["took_ms"] >= 0


async def test_search_treats_free_as_intent_not_a_keyword(client: AsyncClient) -> None:
    response = await client.get(
        "/api/search", params={"q": "free java testing", "page_size": 20}
    )
    body = response.json()
    assert body["meta"]["detected_free_intent"] is True
    assert "free" not in body["meta"]["interpreted_keywords"]
    statuses = {tool["pricing_status"] for tool in body["data"]}
    assert statuses <= set(FREE_PRICING_STATUSES)


async def test_search_ranks_java_testing_tools_first(client: AsyncClient) -> None:
    response = await client.get(
        "/api/search", params={"q": "java unit test generation", "page_size": 10}
    )
    top = response.json()["data"][:5]
    assert any("Java" in tool["languages"] for tool in top)
    assert any("Testing" in tool["features"] for tool in top)


async def test_search_across_categories_and_free_access_text(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/search", params={"q": "kubernetes"})
    slugs = [tool["slug"] for tool in response.json()["data"]]
    assert "k8sgpt" in slugs


async def test_search_with_no_match_returns_empty_page(client: AsyncClient) -> None:
    response = await client.get("/api/search", params={"q": "zzzqqqxyz"})
    body = response.json()
    assert body["data"] == []
    assert body["pagination"]["total"] == 0


async def test_search_facets_count_every_pricing_status(client: AsyncClient) -> None:
    response = await client.get("/api/search", params={"q": "ai"})
    facets = response.json()["facets"]["pricing"]
    assert {facet["value"] for facet in facets} == {
        "FREE_FOREVER",
        "FREE_TIER",
        "FREE_CREDITS",
        "FREE_TRIAL",
        "OPEN_SOURCE",
        "BYOK",
        "PAID_ONLY",
    }


async def test_filter_options_expose_counts(client: AsyncClient) -> None:
    response = await client.get("/api/filters")
    options = response.json()["data"]
    assert len(options["categories"]) >= 30
    assert any(tag["tool_count"] > 0 for tag in options["technologies"])
    assert any(tag["slug"] == "java" for tag in options["technologies"])
    assert [sort["value"] for sort in options["sorts"]]


async def test_sorting_by_name_is_alphabetical(client: AsyncClient) -> None:
    response = await client.get(
        "/api/tools", params={"sort": "name", "page_size": 10}
    )
    names = [tool["name"].lower() for tool in response.json()["data"]]
    assert names == sorted(names)
