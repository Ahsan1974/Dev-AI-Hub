from __future__ import annotations

from httpx import AsyncClient


async def test_compare_returns_aligned_rows(client: AsyncClient) -> None:
    response = await client.post(
        "/api/compare", json={"slugs": ["cursor", "github-copilot", "cline"]}
    )
    assert response.status_code == 200
    payload = response.json()["data"]
    assert [tool["slug"] for tool in payload["tools"]] == [
        "cursor",
        "github-copilot",
        "cline",
    ]
    for row in payload["rows"]:
        assert len(row["cells"]) == 3
    keys = {row["key"] for row in payload["rows"]}
    assert {
        "pricing_status",
        "free_allowance",
        "paid_pricing",
        "is_open_source",
        "has_api",
        "has_mcp",
        "languages",
        "best_for",
    } <= keys


async def test_unknown_values_are_marked_unknown_not_false(
    client: AsyncClient,
) -> None:
    response = await client.post("/api/compare", json={"slugs": ["cursor", "windsurf"]})
    rows = {row["key"]: row for row in response.json()["data"]["rows"]}
    verified = rows["verified"]["cells"][1]
    assert verified["value"] is None
    assert verified["note"] == "Not verified yet"


async def test_compare_reports_missing_slugs(client: AsyncClient) -> None:
    response = await client.post(
        "/api/compare", json={"slugs": ["cursor", "cline", "ghost-tool"]}
    )
    assert response.json()["data"]["missing_slugs"] == ["ghost-tool"]


async def test_compare_rejects_more_than_four_tools(client: AsyncClient) -> None:
    response = await client.post(
        "/api/compare",
        json={"slugs": ["cursor", "cline", "aider", "continue", "zed"]},
    )
    assert response.status_code == 422


async def test_compare_requires_two_existing_tools(client: AsyncClient) -> None:
    response = await client.post("/api/compare", json={"slugs": ["cursor", "nope"]})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "COMPARE_NOT_ENOUGH_TOOLS"


async def test_compare_via_query_string(client: AsyncClient) -> None:
    response = await client.get("/api/compare?slugs=cursor&slugs=cline")
    assert response.status_code == 200
    assert len(response.json()["data"]["tools"]) == 2


async def test_collections_expose_their_tools(client: AsyncClient) -> None:
    listing = await client.get("/api/collections")
    assert len(listing.json()["data"]) >= 8

    detail = await client.get("/api/collections/java-developer-ai-toolkit")
    payload = detail.json()["data"]
    assert payload["tool_count"] == len(payload["tools"])
    assert any("Java" in tool["languages"] for tool in payload["tools"])


async def test_unknown_collection_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/collections/nope")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "COLLECTION_NOT_FOUND"
