from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Favorite(Base, TimestampMixin):
    """A saved tool.

    The MVP has no accounts, so favourites are keyed by an anonymous client id
    generated in the browser. The same table works unchanged once real user ids
    exist - only the column source changes.
    """

    __tablename__ = "favorites"
    __table_args__ = (
        Index("ix_favorites_client_tool", "client_id", "tool_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tool_id: Mapped[int] = mapped_column(
        ForeignKey("tools.id", ondelete="CASCADE"), nullable=False, index=True
    )
