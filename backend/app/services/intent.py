"""Turn a natural language request into structured search signals.

This is the deterministic front half of the recommendation pipeline. An LLM can
later replace or augment :func:`extract_intent` without touching the scorer,
because both sides only exchange :class:`Intent`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.core.enums import TagKind
from app.models.category import Category
from app.models.tag import Tag
from app.utils.text import STOPWORDS, keywords, singularize, tokenize, wants_free

#: Phrases developers actually type, mapped onto taxonomy slugs.
#: Left side is matched against 1-3 word windows of the query.
SYNONYMS: dict[str, list[tuple[str, str]]] = {
    "unit test": [("category", "testing"), ("feature", "testing")],
    "unit tests": [("category", "testing"), ("feature", "testing")],
    "test": [("category", "testing"), ("feature", "testing")],
    "testing": [("category", "testing"), ("feature", "testing")],
    "qa": [("category", "testing")],
    "e2e": [("category", "testing")],
    "bug": [("category", "debugging"), ("feature", "debugging")],
    "bugs": [("category", "debugging"), ("feature", "debugging")],
    "debug": [("category", "debugging"), ("feature", "debugging")],
    "fix": [("category", "debugging")],
    "refactor": [("feature", "refactoring")],
    "review": [("category", "code-review"), ("feature", "code-review")],
    "pr": [("category", "code-review"), ("integration", "github")],
    "autocomplete": [("feature", "code-completion")],
    "completion": [("feature", "code-completion")],
    "write code": [("category", "ai-coding"), ("feature", "code-generation")],
    "code": [("category", "ai-coding"), ("feature", "code-generation")],
    "coding": [("category", "ai-coding"), ("feature", "code-generation")],
    "programming": [("category", "ai-coding")],
    "ide": [("category", "ai-ide")],
    "editor": [("category", "ai-ide")],
    "agent": [("category", "coding-agents"), ("feature", "agents")],
    "agents": [("category", "ai-agents"), ("feature", "agents")],
    "autonomous": [("feature", "agents")],
    "docs": [("category", "documentation"), ("feature", "documentation")],
    "doc": [("category", "documentation"), ("feature", "documentation")],
    "documentation": [("category", "documentation"), ("feature", "documentation")],
    "readme": [("category", "documentation")],
    "api": [("category", "api-development"), ("feature", "api")],
    "rest": [("category", "api-development")],
    "endpoint": [("category", "api-development")],
    "swagger": [("category", "api-development")],
    "openapi": [("category", "api-development")],
    "database": [("category", "database")],
    "db": [("category", "database")],
    "query": [("category", "database")],
    "architecture": [("category", "software-architecture")],
    "design pattern": [("category", "software-architecture")],
    "diagram": [
        ("category", "diagrams-uml"),
        ("category", "software-architecture"),
        ("feature", "architecture-diagrams"),
    ],
    "diagrams": [
        ("category", "diagrams-uml"),
        ("category", "software-architecture"),
    ],
    "uml": [
        ("category", "diagrams-uml"),
        ("feature", "uml"),
        ("feature", "sequence-diagrams"),
        ("feature", "class-diagrams"),
    ],
    "plantuml": [("category", "diagrams-uml"), ("feature", "uml")],
    "mermaid": [("category", "diagrams-uml"), ("feature", "sequence-diagrams")],
    "sequence diagram": [
        ("category", "diagrams-uml"),
        ("feature", "sequence-diagrams"),
    ],
    "sequence diagrams": [
        ("category", "diagrams-uml"),
        ("feature", "sequence-diagrams"),
    ],
    "class diagram": [("category", "diagrams-uml"), ("feature", "class-diagrams")],
    "class diagrams": [("category", "diagrams-uml"), ("feature", "class-diagrams")],
    "draw.io": [("category", "diagrams-uml"), ("category", "non-ai-devtools")],
    "drawio": [("category", "diagrams-uml"), ("category", "non-ai-devtools")],
    "excalidraw": [("category", "whiteboarding"), ("category", "diagrams-uml")],
    "whiteboard": [("category", "whiteboarding")],
    "whiteboarding": [("category", "whiteboarding")],
    "miro": [("category", "whiteboarding")],
    "email": [("category", "email"), ("feature", "email")],
    "emails": [("category", "email"), ("feature", "email")],
    "mail": [("category", "email")],
    "slide": [("category", "presentations"), ("feature", "presentations")],
    "slides": [("category", "presentations"), ("feature", "presentations")],
    "powerpoint": [("category", "presentations")],
    "excel": [("category", "spreadsheets"), ("feature", "spreadsheets")],
    "spreadsheet": [("category", "spreadsheets"), ("feature", "spreadsheets")],
    "spreadsheets": [("category", "spreadsheets")],
    "sheets": [("category", "spreadsheets")],
    "non ai": [("category", "non-ai-devtools")],
    "devtools": [("category", "non-ai-devtools")],
    "devops": [("category", "devops")],
    "deploy": [("category", "devops")],
    "deployment": [("category", "devops")],
    "ci": [("category", "devops")],
    "cicd": [("category", "devops")],
    "pipeline": [("category", "devops")],
    "infrastructure": [("category", "devops")],
    "security": [("category", "security")],
    "vulnerability": [("category", "security")],
    "secrets": [("category", "security")],
    "git": [("category", "git-and-github"), ("integration", "github")],
    "github": [("category", "git-and-github"), ("integration", "github")],
    "commit": [("category", "git-and-github")],
    "productivity": [("category", "developer-productivity")],
    "research": [("category", "research"), ("feature", "research")],
    "paper": [("category", "research")],
    "papers": [("category", "research")],
    "search": [("category", "ai-search"), ("feature", "search")],
    "pdf": [("category", "pdf-analysis")],
    "document": [("category", "pdf-analysis")],
    "chatbot": [("category", "general-ai")],
    "chat": [("category", "general-ai")],
    "assistant": [("category", "general-ai")],
    "image": [("category", "image-generation"), ("feature", "image-generation")],
    "images": [("category", "image-generation"), ("feature", "image-generation")],
    "picture": [("category", "image-generation")],
    "photo": [("category", "image-editing")],
    "logo": [("category", "image-generation")],
    "art": [("category", "image-generation")],
    "background": [("category", "image-editing"), ("feature", "image-editing")],
    "upscale": [("category", "image-editing")],
    "video": [("category", "video-generation"), ("feature", "video-generation")],
    "videos": [("category", "video-generation")],
    "clip": [("category", "video-editing")],
    "subtitle": [("category", "video-editing")],
    "audio": [("category", "audio"), ("feature", "audio-generation")],
    "sound": [("category", "audio")],
    "speech": [("category", "voice"), ("feature", "speech")],
    "tts": [("category", "voice"), ("feature", "speech")],
    "voice": [("category", "voice"), ("feature", "voice")],
    "voiceover": [("category", "voice")],
    "transcribe": [("category", "audio"), ("feature", "speech")],
    "transcription": [("category", "audio"), ("feature", "speech")],
    "music": [("category", "music"), ("feature", "music")],
    "song": [("category", "music")],
    "ui": [("category", "ui-ux"), ("feature", "ui-generation")],
    "frontend": [("category", "ui-ux"), ("feature", "ui-generation")],
    "interface": [("category", "ui-ux")],
    "component": [("category", "ui-ux"), ("feature", "ui-generation")],
    "design": [("category", "design")],
    "mockup": [("category", "design")],
    "wireframe": [("category", "design")],
    "presentation": [("category", "presentations")],
    "slide": [("category", "presentations")],
    "slides": [("category", "presentations")],
    "deck": [("category", "presentations")],
    "writing": [("category", "writing")],
    "blog": [("category", "writing")],
    "content": [("category", "writing")],
    "llm": [("category", "llm-development")],
    "prompt": [("category", "llm-development")],
    "finetune": [("category", "llm-development")],
    "fine tuning": [("category", "llm-development")],
    "rag": [("category", "rag"), ("feature", "rag")],
    "embedding": [("category", "rag")],
    "embeddings": [("category", "rag")],
    "vector": [("category", "rag")],
    "mcp": [("category", "mcp"), ("feature", "mcp")],
    "local": [("category", "local-ai"), ("feature", "local-models")],
    "offline": [("category", "local-ai"), ("feature", "local-models")],
    "self hosted": [("category", "local-ai")],
    "open source": [("category", "open-source-ai")],
    "learn": [("category", "learning")],
    "learning": [("category", "learning")],
    "tutorial": [("category", "learning")],
    "study": [("category", "learning")],
    "notes": [("category", "productivity")],
    "meeting": [("category", "productivity")],
    "note taking": [("category", "productivity")],
}

#: Explicit technology aliases that tokenization alone would miss.
TECH_ALIASES: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "golang": "go",
    "cpp": "cpp",
    "csharp": "csharp",
    "dotnet": "csharp",
    "postgres": "postgresql",
    "psql": "postgresql",
    "k8s": "kubernetes",
    "springboot": "spring-boot",
    "spring": "spring-boot",
    "nodejs": "node-js",
    "node": "node-js",
    "vscode": "vs-code",
    "intellij": "intellij-idea",
    "jetbrains": "intellij-idea",
    "reactjs": "react",
    "nextjs": "react",
}


@dataclass(slots=True)
class Intent:
    raw_query: str
    keywords: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    integrations: list[str] = field(default_factory=list)
    free_intent: bool = False


class TaxonomyIndex:
    """Lookup from a word to the taxonomy entries it can refer to."""

    def __init__(self, categories: list[Category], tags: list[Tag]) -> None:
        self.category_slugs = {category.slug for category in categories}
        self.tag_slugs: dict[str, set[str]] = {
            TagKind.TECHNOLOGY: set(),
            TagKind.FEATURE: set(),
            TagKind.PLATFORM: set(),
            TagKind.INTEGRATION: set(),
        }
        self._words: dict[str, set[tuple[str, str]]] = {}

        for category in categories:
            self._index_entry("category", category.slug, category.name, category.slug)
        for tag in tags:
            self.tag_slugs.setdefault(tag.kind, set()).add(tag.slug)
            self._index_entry(tag.kind, tag.slug, tag.name, tag.slug)

    def _index_entry(self, kind: str, slug: str, *sources: str) -> None:
        for source in sources:
            for word in set(tokenize(source.replace("-", " "))):
                if len(word) < 2:
                    continue
                self._words.setdefault(word, set()).add((kind, slug))
                self._words.setdefault(singularize(word), set()).add((kind, slug))

    def lookup(self, word: str) -> set[tuple[str, str]]:
        return self._words.get(word, set()) | self._words.get(singularize(word), set())

    def has(self, kind: str, slug: str) -> bool:
        if kind == "category":
            return slug in self.category_slugs
        return slug in self.tag_slugs.get(kind, set())


def _phrases(tokens: list[str]) -> list[str]:
    result = list(tokens)
    result += [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]
    return result


def extract_intent(query: str, index: TaxonomyIndex) -> Intent:
    """Map free text onto category / technology / feature slugs.

    Two passes: curated synonyms (handles "unit tests" -> testing) followed by a
    direct match against the live taxonomy (handles any seeded tag name).
    """
    tokens = tokenize(query)
    buckets: dict[str, list[str]] = {
        "category": [],
        TagKind.TECHNOLOGY: [],
        TagKind.FEATURE: [],
        TagKind.PLATFORM: [],
        TagKind.INTEGRATION: [],
    }

    def push(kind: str, slug: str) -> None:
        bucket = buckets.setdefault(kind, [])
        if slug not in bucket and index.has(kind, slug):
            bucket.append(slug)

    for phrase in _phrases(tokens):
        entries = SYNONYMS.get(phrase) or SYNONYMS.get(singularize(phrase), [])
        for kind, slug in entries:
            push(kind, slug)
        alias = TECH_ALIASES.get(phrase.replace(" ", ""))
        if alias:
            push(TagKind.TECHNOLOGY, alias)

    # Generic words like "ai" or "tool" appear in most taxonomy names and would
    # otherwise match nearly every category, diluting the score denominator.
    for word in tokens:
        if word in STOPWORDS or len(word) < 3:
            continue
        for kind, slug in index.lookup(word):
            push(kind, slug)

    return Intent(
        raw_query=query,
        keywords=keywords(query),
        categories=buckets["category"],
        technologies=buckets[TagKind.TECHNOLOGY],
        features=buckets[TagKind.FEATURE],
        platforms=buckets[TagKind.PLATFORM],
        integrations=buckets[TagKind.INTEGRATION],
        free_intent=wants_free(query),
    )
