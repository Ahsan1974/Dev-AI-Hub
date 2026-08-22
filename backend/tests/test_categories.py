from __future__ import annotations

from httpx import AsyncClient


async def test_categories_include_tool_counts(client: AsyncClient) -> None:
    response = await client.get("/api/categories")
    categories = response.json()["data"]
    assert len(categories) >= 30
    testing = next(item for item in categories if item["slug"] == "testing")
    assert testing["tool_count"] > 0
    assert testing["free_tool_count"] <= testing["tool_count"]
    assert testing["group"] == "Software Development"


async def test_category_tools_are_filtered_to_that_category(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/categories/image-generation/tools", params={"page_size": 30}
    )
    assert response.status_code == 200
    tools = response.json()["data"]
    assert tools
    for tool in tools:
        assert "image-generation" in {c["slug"] for c in tool["categories"]}


async def test_category_tools_accept_additional_filters(client: AsyncClient) -> None:
    response = await client.get(
        "/api/categories/image-generation/tools",
        params={"pricing": "OPEN_SOURCE", "page_size": 30},
    )
    tools = response.json()["data"]
    assert tools
    assert {tool["pricing_status"] for tool in tools} == {"OPEN_SOURCE"}


async def test_unknown_category_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/categories/not-real/tools")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CATEGORY_NOT_FOUND"
