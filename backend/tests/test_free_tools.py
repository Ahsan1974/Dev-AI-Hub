from __future__ import annotations

from httpx import AsyncClient


async def test_free_tools_sections_group_by_how_they_are_free(
    client: AsyncClient,
) -> None:
    response = await client.get("/api/free-tools")
    payload = response.json()["data"]
    sections = {section["slug"]: section for section in payload["sections"]}
    assert set(sections) == {
        "completely-free",
        "open-source",
        "generous-free-tiers",
        "free-credits",
        "free-developer-apis",
    }
    assert {tool["pricing_status"] for tool in sections["open-source"]["tools"]} == {
        "OPEN_SOURCE"
    }
    assert all(
        tool["pricing_status"] == "FREE_FOREVER"
        for tool in sections["completely-free"]["tools"]
    )
    assert all(
        tool["flags"]["has_free_api"]
        for tool in sections["free-developer-apis"]["tools"]
    )


async def test_free_tools_can_be_filtered_by_category(client: AsyncClient) -> None:
    response = await client.get("/api/free-tools", params={"category": "testing"})
    payload = response.json()["data"]
    assert payload["active_category"] == "testing"
    for section in payload["sections"]:
        for tool in section["tools"]:
            assert "testing" in {c["slug"] for c in tool["categories"]}


async def test_home_never_invents_favourites(client: AsyncClient) -> None:
    response = await client.get("/api/home")
    payload = response.json()["data"]
    assert payload["stats"]["tools"] >= 500
    assert payload["stats"]["free_tools"] > 0
    assert payload["favorites_available"] is False
    assert payload["developer_favorites"] == []
    assert len(payload["workflows"]) == 12
    assert payload["popular_searches"]


async def test_recently_added_is_ordered_by_creation_time(client: AsyncClient) -> None:
    response = await client.get("/api/home")
    recent = response.json()["data"]["recently_added"]
    timestamps = [tool["created_at"] for tool in recent]
    assert timestamps == sorted(timestamps, reverse=True)


async def test_favorites_require_a_client_id(client: AsyncClient) -> None:
    response = await client.get("/api/favorites")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "CLIENT_ID_REQUIRED"


async def test_favorites_round_trip_for_an_anonymous_client(
    client: AsyncClient,
) -> None:
    headers = {"X-Client-Id": "test-device-1"}
    assert (await client.put("/api/favorites/ollama", headers=headers)).status_code == 200
    listed = await client.get("/api/favorites", headers=headers)
    assert [tool["slug"] for tool in listed.json()["data"]] == ["ollama"]
    await client.delete("/api/favorites/ollama", headers=headers)
    listed = await client.get("/api/favorites", headers=headers)
    assert listed.json()["data"] == []
