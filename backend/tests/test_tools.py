from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.enums import FREE_PRICING_STATUSES


async def test_list_tools_uses_the_standard_envelope(client: AsyncClient) -> None:
    response = await client.get("/api/tools", params={"page": 1, "page_size": 5})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"data", "pagination"}
    assert len(body["data"]) == 5
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["total"] >= 500
    assert body["pagination"]["has_previous"] is False


async def test_pagination_returns_distinct_pages(client: AsyncClient) -> None:
    first = await client.get("/api/tools", params={"page": 1, "page_size": 4})
    second = await client.get("/api/tools", params={"page": 2, "page_size": 4})
    first_slugs = [tool["slug"] for tool in first.json()["data"]]
    second_slugs = [tool["slug"] for tool in second.json()["data"]]
    assert not set(first_slugs) & set(second_slugs)
    assert second.json()["pagination"]["has_previous"] is True


async def test_page_size_is_capped(client: AsyncClient) -> None:
    response = await client.get("/api/tools", params={"page_size": 5000})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_tool_detail_exposes_free_access_and_verification(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/tools/cursor")
    assert response.status_code == 200
    tool = response.json()["data"]
    assert tool["slug"] == "cursor"
    assert tool["pricing"]["is_free"] is True
    assert tool["free_access_lines"]
    assert tool["verification"]["is_verified"] is True
    assert tool["quality"]["score"] > 0
    assert "Java" in tool["languages"]


async def test_unverified_tool_reports_missing_pricing_honestly(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/tools/windsurf")
    tool = response.json()["data"]
    assert tool["verification"]["is_verified"] is False
    assert tool["pricing_plans"] == []
    assert "official pricing page" in tool["pricing_summary"].lower()


async def test_paid_only_tool_is_not_presented_as_free(client: AsyncClient) -> None:
    response = await client.get("/api/tools/midjourney")
    tool = response.json()["data"]
    assert tool["pricing_status"] == "PAID_ONLY"
    assert tool["pricing"]["is_free"] is False
    assert any(line["kind"] == "warn" for line in tool["free_access_lines"])


async def test_missing_tool_returns_structured_error(client: AsyncClient) -> None:
    response = await client.get("/api/tools/not-a-real-tool")
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "TOOL_NOT_FOUND",
            "message": "No tool exists with the slug 'not-a-real-tool'.",
        }
    }


async def test_alternatives_exclude_the_tool_itself(client: AsyncClient) -> None:
    response = await client.get("/api/tools/cursor/alternatives", params={"limit": 5})
    assert response.status_code == 200
    slugs = [tool["slug"] for tool in response.json()["data"]]
    assert slugs and "cursor" not in slugs


async def test_pricing_endpoint_carries_a_disclaimer(client: AsyncClient) -> None:
    response = await client.get("/api/tools/github-copilot/pricing")
    payload = response.json()["data"]
    assert payload["plans"]
    assert payload["last_verified_at"] is not None
    assert payload["verification_source_url"]
    assert "official pricing page" in payload["disclaimer"].lower()


async def test_free_only_filter_returns_only_free_statuses(client: AsyncClient) -> None:
    response = await client.get(
        "/api/tools", params={"free_only": True, "page_size": 50}
    )
    statuses = {tool["pricing_status"] for tool in response.json()["data"]}
    assert statuses
    assert statuses <= set(FREE_PRICING_STATUSES)


@pytest.mark.parametrize(
    "params,expected",
    [
        ({"technology": "java"}, "languages"),
        ({"feature": "testing"}, "features"),
        ({"platform": "cli"}, "platforms"),
    ],
)
async def test_tag_filters_narrow_results(
    client: AsyncClient, params: dict, expected: str
) -> None:
    response = await client.get("/api/tools", params={**params, "page_size": 50})
    assert response.status_code == 200
    data = response.json()["data"]
    assert data
    assert all(tool[expected] for tool in data)


async def test_resolve_preserves_requested_order(client: AsyncClient) -> None:
    response = await client.post(
        "/api/tools/resolve", json={"slugs": ["ollama", "cursor", "nope"]}
    )
    assert [tool["slug"] for tool in response.json()["data"]] == ["ollama", "cursor"]
