"""Curated developer workflows and query presets.

Defined server-side so the homepage, the "What do I need?" presets and the stack
builder all agree on the same taxonomy slugs.
"""

from __future__ import annotations

from pydantic import BaseModel


class Workflow(BaseModel):
    slug: str
    label: str
    description: str
    icon: str
    query: str
    categories: list[str] = []


WORKFLOWS: list[Workflow] = [
    Workflow(
        slug="write-code",
        label="Write Code",
        description="Generate and complete code inside your editor.",
        icon="code",
        query="write and generate code with AI",
        categories=["ai-coding", "code-generation", "ai-ide"],
    ),
    Workflow(
        slug="debug-code",
        label="Debug Code",
        description="Find and explain the cause of failures.",
        icon="bug",
        query="debug and fix errors in my code",
        categories=["debugging"],
    ),
    Workflow(
        slug="generate-tests",
        label="Generate Tests",
        description="Create unit and integration tests automatically.",
        icon="flask",
        query="generate unit tests for my code",
        categories=["testing"],
    ),
    Workflow(
        slug="review-code",
        label="Review Code",
        description="Automated pull request and code quality review.",
        icon="check",
        query="review my pull requests automatically",
        categories=["code-review"],
    ),
    Workflow(
        slug="generate-documentation",
        label="Generate Documentation",
        description="Turn code into readable docs and READMEs.",
        icon="book",
        query="generate documentation from my codebase",
        categories=["documentation"],
    ),
    Workflow(
        slug="build-ui",
        label="Build UI",
        description="Generate interfaces and frontend components.",
        icon="layout",
        query="generate UI components for my web app",
        categories=["ui-ux", "design"],
    ),
    Workflow(
        slug="research",
        label="Research",
        description="Search papers, docs and the web with citations.",
        icon="search",
        query="research technical topics with sources",
        categories=["research", "ai-search"],
    ),
    Workflow(
        slug="generate-images",
        label="Generate Images",
        description="Create and edit images and assets.",
        icon="image",
        query="generate images for free",
        categories=["image-generation", "image-editing"],
    ),
    Workflow(
        slug="generate-videos",
        label="Generate Videos",
        description="Create or edit video content.",
        icon="video",
        query="generate video from text",
        categories=["video-generation", "video-editing"],
    ),
    Workflow(
        slug="generate-audio",
        label="Generate Audio",
        description="Speech, voice and music generation.",
        icon="audio",
        query="generate speech and voice audio",
        categories=["audio", "voice", "music"],
    ),
    Workflow(
        slug="deploy",
        label="Deploy",
        description="Ship, automate and operate infrastructure.",
        icon="rocket",
        query="deploy and automate my infrastructure",
        categories=["devops"],
    ),
    Workflow(
        slug="learn",
        label="Learn",
        description="Learn new technologies faster.",
        icon="graduation",
        query="learn a new programming technology",
        categories=["learning"],
    ),
]

POPULAR_SEARCHES: list[str] = [
    "AI coding",
    "Java development",
    "Free image generator",
    "AI video generator",
    "Code testing",
    "AI research",
    "API documentation",
    "UI generation",
]

#: Areas used by the personal stack builder, in presentation order.
STACK_AREAS: list[dict[str, object]] = [
    {
        "slug": "coding",
        "area": "Coding",
        "description": "Day-to-day code generation and completion.",
        "categories": ["ai-coding", "ai-ide", "code-generation"],
        "query": "write code faster in my editor",
    },
    {
        "slug": "agents",
        "area": "Coding agents",
        "description": "Delegate multi-step changes across your repository.",
        "categories": ["coding-agents"],
        "query": "autonomous coding agent for my repository",
    },
    {
        "slug": "debugging",
        "area": "Debugging",
        "description": "Understand failures and stack traces.",
        "categories": ["debugging"],
        "query": "debug errors and exceptions",
    },
    {
        "slug": "testing",
        "area": "Testing",
        "description": "Generate and maintain automated tests.",
        "categories": ["testing"],
        "query": "generate unit tests",
    },
    {
        "slug": "code-review",
        "area": "Code review",
        "description": "Catch issues before they reach main.",
        "categories": ["code-review"],
        "query": "automated code review on pull requests",
    },
    {
        "slug": "documentation",
        "area": "Documentation",
        "description": "Keep docs close to the code.",
        "categories": ["documentation"],
        "query": "generate and maintain documentation",
    },
    {
        "slug": "research",
        "area": "Research",
        "description": "Answer technical questions with sources.",
        "categories": ["research", "ai-search"],
        "query": "research technical questions with citations",
    },
    {
        "slug": "ui",
        "area": "UI",
        "description": "Generate frontend components and layouts.",
        "categories": ["ui-ux", "design"],
        "query": "generate UI components",
    },
    {
        "slug": "devops",
        "area": "DevOps",
        "description": "Automate builds, pipelines and infrastructure.",
        "categories": ["devops"],
        "query": "automate deployment and infrastructure",
    },
    {
        "slug": "productivity",
        "area": "Productivity",
        "description": "Notes, meetings and everyday assistance.",
        "categories": ["developer-productivity", "productivity", "general-ai"],
        "query": "general assistant for developer productivity",
    },
]
