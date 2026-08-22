"""Prepare a writable SQLite file for serverless hosts (e.g. Vercel /tmp)."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger("devai_hub")


def _sqlite_path_from_url(url: str) -> Path | None:
    if not url.startswith("sqlite"):
        return None
    # sqlite+aiosqlite:///./file.db  -> ./file.db
    # sqlite+aiosqlite:////tmp/x.db  -> /tmp/x.db
    if ":///" not in url:
        return None
    raw = url.split(":///", 1)[1]
    return Path(raw)


def prepare_sqlite_database() -> None:
    """Copy the bundled catalogue into the runtime SQLite path when missing."""
    dest = _sqlite_path_from_url(settings.database_url)
    if dest is None:
        return
    if dest.exists() and dest.stat().st_size > 0:
        return

    bundled = Path(__file__).resolve().parents[2] / "data" / "catalogue.db"
    if not bundled.exists():
        logger.warning(
            "No bundled catalogue at %s — empty DB will be created at %s",
            bundled,
            dest,
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bundled, dest)
    logger.info("Copied bundled catalogue (%s bytes) → %s", bundled.stat().st_size, dest)
