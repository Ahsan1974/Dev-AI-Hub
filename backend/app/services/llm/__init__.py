"""Optional LLM layer.

The MVP never depends on this package: :func:`get_provider` returns a null
provider unless ``LLM_PROVIDER`` is configured, and every caller degrades to the
deterministic rule-based path.
"""

from app.services.llm.base import (
    LLMProvider,
    NullLLMProvider,
    RankedCandidate,
    get_provider,
)

__all__ = ["LLMProvider", "NullLLMProvider", "RankedCandidate", "get_provider"]
