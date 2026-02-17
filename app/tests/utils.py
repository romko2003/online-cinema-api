from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def truncate_all_tables(session: AsyncSession) -> None:
    """
    Fast Postgres cleanup between tests.
    Truncates all public tables except alembic_version.
    """
    res = await session.execute(
        text(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
              AND tablename <> 'alembic_version';
            """
        )
    )
    tables = [row[0] for row in res.fetchall()]

    if not tables:
        return

    # TRUNCATE ... CASCADE resets dependent rows too
    quoted = ", ".join(f'"{t}"' for t in tables)
    await session.execute(text(f"TRUNCATE TABLE {quoted} RESTART IDENTITY CASCADE;"))
    await session.commit()
