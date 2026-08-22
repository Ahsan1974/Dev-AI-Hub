import json
from pathlib import Path

from app.core.enums import FREE_PRICING_STATUSES, PricingStatus
from app.seed.seeder import load_tool_data

tools = load_tool_data()
cats = {
    c["slug"]
    for c in json.loads(Path("app/seed/data/categories.json").read_text(encoding="utf-8"))
}
valid_status = {s.value for s in PricingStatus}
errors: list[tuple[str, str]] = []
for tool in tools:
    name = tool.get("name", "?")
    if not tool.get("website_url"):
        errors.append((name, "no website"))
    if tool.get("pricing_status") not in valid_status:
        errors.append((name, f"bad status {tool.get('pricing_status')}"))
    unknown = set(tool.get("categories", [])) - cats
    if unknown:
        errors.append((name, f"unknown {unknown}"))
    priced = [
        plan
        for plan in tool.get("pricing_plans", [])
        if plan.get("price") not in (None, 0)
    ]
    if priced and not tool.get("verification_source_url"):
        errors.append((name, "priced unverified"))

print("tools", len(tools), "unique", len({t["name"].lower() for t in tools}))
print("errors", len(errors))
for item in errors[:20]:
    print(item)
free = sum(1 for t in tools if t.get("pricing_status") in FREE_PRICING_STATUSES)
print(f"free {free} ({free / len(tools):.1%})")
print("statuses", sorted({t["pricing_status"] for t in tools}))
print("categories", len(cats))
