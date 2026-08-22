from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Owns a session; subclasses expose intention-revealing query methods."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @property
    def dialect(self) -> str:
        try:
            return self.session.get_bind().dialect.name
        except Exception:  # pragma: no cover - unbound session in unit tests
            return "sqlite"

    @property
    def is_postgres(self) -> bool:
        return self.dialect == "postgresql"
