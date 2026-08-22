"""Quick end-to-end check against a running server.

Usage: python scripts/smoke.py [base_url]
"""

from __future__ import annotations

import json
import sys

import httpx

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

CHECKS: list[tuple[str, str, dict | None]] = [
    ("GET", "/api/health", None),
    ("GET", "/api/home", None),
    ("GET", "/api/tools?page=1&page_size=3", None),
    ("GET", "/api/tools/cursor", None),
    ("GET", "/api/tools/cursor/alternatives", None),
    ("GET", "/api/tools/cursor/pricing", None),
    ("GET", "/api/tools/does-not-exist", None),
    ("GET", "/api/categories", None),
    ("GET", "/api/categories/testing/tools?page_size=3", None),
    ("GET", "/api/search?q=free+java+unit+testing&page_size=5", None),
    ("GET", "/api/filters", None),
    ("GET", "/api/free-tools?limit=3", None),
    ("GET", "/api/collections", None),
    ("GET", "/api/collections/java-developer-ai-toolkit", None),
    ("GET", "/api/meta", None),
    (
        "POST",
        "/api/recommendations",
        {"query": "I need a free AI tool to generate Java unit tests", "budget": "free_only"},
    ),
    (
        "POST",
        "/api/recommendations/stack",
        {"primary_language": "Java", "frameworks": ["Spring Boot"], "ide": "IntelliJ IDEA", "budget": "free_only"},
    ),
    ("POST", "/api/compare", {"slugs": ["cursor", "github-copilot", "cline"]}),
    ("POST", "/api/admin/tools", {"name": "Nope", "website_url": "https://example.com"}),
]


def summarise(path: str, payload: object) -> str:
    if not isinstance(payload, dict):
        return str(payload)[:120]
    if "error" in payload:
        return f"error={payload['error']['code']}"
    data = payload.get("data")
    if isinstance(data, list):
        return f"data[{len(data)}]"
    if isinstance(data, dict):
        keys = list(data)[:6]
        return f"keys={keys}"
    if "pagination" in payload:
        return f"data[{len(payload.get('data', []))}] total={payload['pagination']['total']}"
    return json.dumps(payload)[:120]


def main() -> int:
    failures = 0
    with httpx.Client(base_url=BASE, timeout=30) as client:
        for method, path, body in CHECKS:
            try:
                response = client.request(method, path, json=body)
            except Exception as exc:  # pragma: no cover - smoke script
                print(f"FAIL {method} {path} -> {exc}")
                failures += 1
                continue
            marker = "ok " if response.status_code < 500 else "FAIL"
            if response.status_code >= 500:
                failures += 1
            try:
                payload = response.json()
            except Exception:
                payload = response.text
            print(f"{marker} {response.status_code} {method} {path} :: {summarise(path, payload)}")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
