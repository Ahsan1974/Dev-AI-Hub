"""Text helpers used by slugs, search and the recommendation engine."""

from __future__ import annotations

import re
import unicodedata

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")
_TOKEN = re.compile(r"[a-z0-9\+#\.]+")

#: Words that carry no ranking signal for tool discovery queries.
STOPWORDS: frozenset[str] = frozenset(
    """
    a an and are as at be best but by can could do does for from get good great have
    help i im i'm in is it its me my need needs of on or please recommend recommended
    should show some that the their them there these they this to tool tools use used
    using want was what when where which who will with without would you your ai
    something looking find find's give
    """.split()
)

#: Query words that express a free-only intent.
FREE_INTENT_WORDS: frozenset[str] = frozenset(
    {
        "free",
        "freely",
        "gratis",
        "cheap",
        "budget",
        "no-cost",
        "nocost",
        "opensource",
        "open-source",
        "foss",
        "selfhosted",
        "self-hosted",
        "self-host",
        "zero",
    }
)


def slugify(value: str, *, max_length: int = 180) -> str:
    """Return a URL safe slug.

    ``C++`` becomes ``cpp`` and ``C#`` becomes ``csharp`` so technology slugs stay
    readable instead of collapsing to ``c``.
    """
    value = value.strip().lower()
    value = value.replace("c++", "cpp").replace("c#", "csharp")
    value = value.replace("&", " and ").replace("+", " plus ").replace("#", " sharp ")
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = _SLUG_STRIP.sub("-", value).strip("-")
    return value[:max_length] or "item"


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens, keeping ``c++``/``c#``/``node.js`` intact."""
    if not text:
        return []
    lowered = text.lower().replace("c++", "cpp").replace("c#", "csharp")
    return _TOKEN.findall(lowered)


def keywords(text: str, *, min_length: int = 2) -> list[str]:
    """Meaningful tokens with stopwords and noise removed, order preserved."""
    seen: set[str] = set()
    result: list[str] = []
    for token in tokenize(text):
        token = token.strip(".")
        if len(token) < min_length or token in STOPWORDS or token in seen:
            continue
        seen.add(token)
        result.append(token)
    return result


def singularize(token: str) -> str:
    """Naive singular form good enough for matching "tests" to "test"."""
    if len(token) > 3 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 3 and token.endswith("sses"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def wants_free(text: str) -> bool:
    """True when the wording signals a free-only intent.

    Bigrams are checked too so "open source" and "self hosted" are recognised
    regardless of whether the user hyphenated them.
    """
    tokens = tokenize(text)
    bigrams = [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]
    candidates = set(tokens) | {bigram.replace(" ", "-") for bigram in bigrams}
    return bool(candidates & FREE_INTENT_WORDS)


def truncate(text: str, limit: int = 180) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "\u2026"


def initials(name: str) -> str:
    parts = [part for part in re.split(r"[\s\-_/.]+", name.strip()) if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()
