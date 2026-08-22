"""Many-to-many association tables."""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, Table

from app.db.base import Base

tool_categories = Table(
    "tool_categories",
    Base.metadata,
    Column(
        "tool_id",
        ForeignKey("tools.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column(
        "category_id",
        ForeignKey("categories.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)

tool_tags = Table(
    "tool_tags",
    Base.metadata,
    Column(
        "tool_id",
        ForeignKey("tools.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)

collection_tools = Table(
    "collection_tools",
    Base.metadata,
    Column(
        "collection_id",
        ForeignKey("collections.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column(
        "tool_id",
        ForeignKey("tools.id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
    Column("position", Integer, nullable=False, default=0),
)
