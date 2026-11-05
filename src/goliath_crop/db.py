"""Shared database connection helpers for domain actions and workers."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg


def libpq_configured() -> bool:
    return bool(os.environ.get("PGHOST") and os.environ.get("PGDATABASE") and os.environ.get("PGUSER"))


@contextmanager
def connect(
    *,
    user: Optional[str] = None,
) -> Generator[psycopg.Connection, None, None]:
    if not libpq_configured():
        raise RuntimeError("Set PGHOST, PGDATABASE, and PGUSER for database access")
    with psycopg.connect(
        host=os.environ["PGHOST"],
        port=os.environ.get("PGPORT", "5432"),
        dbname=os.environ["PGDATABASE"],
        user=user or os.environ["PGUSER"],
        password=os.environ.get("PGPASSWORD"),
    ) as conn:
        yield conn


def user_id_from_context(context: dict[str, object] | None) -> int | None:
    if not context:
        return None
    raw = context.get("user_id") or context.get("session_user_id")
    if raw is None:
        return None
    if not isinstance(raw, (int, str)):
        return None
    return int(raw)
