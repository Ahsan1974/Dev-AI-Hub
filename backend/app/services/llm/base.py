"""Provider contract for future LLM-assisted ranking.

Pipeline once a provider is configured::

    user query -> extract intent -> generate search terms -> database retrieval
    -> metadata filtering -> LLM ranking -> explanation

Only the last two steps live here; everything before them already works without
an API key.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from app.core.config import settings


@dataclass(slots=True)
class RankedCandidate:
    slug: str
    score: int
    explanation: str


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    @property
    def available(self) -> bool: ...

    async def rerank(
        self, query: str, candidates: list[dict], limit: int
    ) -> list[RankedCandidate]: ...


class NullLLMProvider:
    """Always unavailable. Keeps call sites free of ``if provider is None``."""

    name = "none"

    @property
    def available(self) -> bool:
        return False

    async def rerank(
        self, query: str, candidates: list[dict], limit: int
    ) -> list[RankedCandidate]:
        return []


class OpenAIProvider(NullLLMProvider):
    """Placeholder wired to configuration but intentionally not implemented.

    Implement ``rerank`` by sending ``candidates`` (slug + summary + pricing) and
    asking for a ranked JSON array. Never send anything beyond public tool data.
    """

    name = "openai"

    @property
    def available(self) -> bool:
        return bool(settings.openai_api_key)


class OllamaProvider(NullLLMProvider):
    """Placeholder for a fully local re-ranker via Ollama."""

    name = "ollama"

    @property
    def available(self) -> bool:
        return bool(settings.ollama_base_url)


def get_provider() -> LLMProvider:
    if settings.llm_provider == "openai":
        return OpenAIProvider()
    if settings.llm_provider == "ollama":
        return OllamaProvider()
    return NullLLMProvider()
