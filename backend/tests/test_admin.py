from __future__ import annotations

from httpx import AsyncClient

NEW_TOOL = {
    "name": "Example Test Tool",
    "tagline": "Fixture tool",
    "description": "A tool created by the admin API test.",
    "website_url": "https://example.com",
    "pricing_status": "FREE_TIER",
    "free_access_summary": "Free tier with limits.",
    "categories": ["testing"],
    "technologies": ["Java"],
    "features": ["Testing"],
    "free_access": [
        {
            "type": "ALLOWANCE",
            "amount": 100,
            "unit": "requests",
            "period": "month",
            "requires_credit_card": False,
        }
    ],
}


async def test_admin_is_disabled_without_a_configured_key(client: AsyncClient) -> None:
    response = await client.post("/api/admin/tools", json=NEW_TOOL)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "ADMIN_DISABLED"


async def test_admin_rejects_a_wrong_key(
    client: AsyncClient, admin_headers: dict
) -> None:
    response = await client.post(
        "/api/admin/tools", json=NEW_TOOL, headers={"X-Admin-Api-Key": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_admin_can_create_update_and_delete_a_tool(
    client: AsyncClient, admin_headers: dict
) -> None:
    created = await client.post("/api/admin/tools", json=NEW_TOOL, headers=admin_headers)
    assert created.status_code == 201
    tool = created.json()["data"]
    assert tool["slug"] == "example-test-tool"
    assert tool["languages"] == ["Java"]
    assert tool["free_access_lines"][0]["text"] == "100 requests / month"

    # The new tool is immediately searchable, so search_text was rebuilt.
    found = await client.get("/api/search", params={"q": "fixture tool"})
    assert "example-test-tool" in [item["slug"] for item in found.json()["data"]]

    updated = await client.patch(
        "/api/admin/tools/example-test-tool",
        json={"pricing_status": "PAID_ONLY", "featured": True},
        headers=admin_headers,
    )
    assert updated.json()["data"]["pricing_status"] == "PAID_ONLY"
    assert updated.json()["data"]["featured"] is True

    deleted = await client.delete(
        "/api/admin/tools/example-test-tool", headers=admin_headers
    )
    assert deleted.status_code == 200
    assert (await client.get("/api/tools/example-test-tool")).status_code == 404


async def test_admin_rejects_a_duplicate_slug(
    client: AsyncClient, admin_headers: dict
) -> None:
    response = await client.post(
        "/api/admin/tools",
        json={**NEW_TOOL, "name": "Cursor"},
        headers=admin_headers,
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


async def test_admin_rejects_an_unknown_category(
    client: AsyncClient, admin_headers: dict
) -> None:
    response = await client.post(
        "/api/admin/tools",
        json={**NEW_TOOL, "name": "Bad Category Tool", "categories": ["nope"]},
        headers=admin_headers,
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNKNOWN_CATEGORY"


async def test_admin_rejects_a_non_http_website(
    client: AsyncClient, admin_headers: dict
) -> None:
    response = await client.post(
        "/api/admin/tools",
        json={**NEW_TOOL, "name": "Bad URL Tool", "website_url": "javascript:alert(1)"},
        headers=admin_headers,
    )
    assert response.status_code == 422
