"""Akses database sebagai role runtime (bussn_app).

Dua pintu masuk:
- plain_session(): untuk tabel tingkat pengguna (users, consents, refresh_tokens).
- tenant_session(business_id): untuk tabel milik usaha. Mengatur app.business_id
  di dalam transaksi sehingga policy RLS membatasi baris ke usaha itu saja.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        engine = create_async_engine(get_settings().app_database_url, pool_pre_ping=True)
        _sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    return _sessionmaker


@asynccontextmanager
async def plain_session(
    sm: async_sessionmaker[AsyncSession] | None = None,
) -> AsyncIterator[AsyncSession]:
    async with (sm or get_sessionmaker())() as session, session.begin():
        yield session


@asynccontextmanager
async def tenant_session(
    business_id: UUID,
    sm: async_sessionmaker[AsyncSession] | None = None,
) -> AsyncIterator[AsyncSession]:
    async with (sm or get_sessionmaker())() as session, session.begin():
        # is_local=true: nilai hanya hidup sampai transaksi ini selesai,
        # jadi aman terhadap connection pool.
        await session.execute(
            text("SELECT set_config('app.business_id', :bid, true)"),
            {"bid": str(business_id)},
        )
        yield session
