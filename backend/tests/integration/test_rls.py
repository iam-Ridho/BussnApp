"""Uji isolasi RLS pada Postgres sungguhan.
Prasyarat: docker compose up -d && make migrate"""

import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.db import plain_session, tenant_session

pytestmark = pytest.mark.integration


@pytest.fixture
def seeded():
    """Dua usaha dengan masing-masing 2 transaksi, dibuat lewat role pemilik (melewati RLS)."""
    eng = create_engine(get_settings().migrator_database_url, poolclass=NullPool)
    tag = uuid.uuid4().hex[:8]
    data = {}
    try:
        with eng.begin() as c:
            c.execute(text("SELECT 1 FROM transactions LIMIT 0"))
    except Exception:
        pytest.skip("Database belum termigrasi: jalankan `make migrate`")
    with eng.begin() as c:
        for name in ("a", "b"):
            uid = c.execute(
                text("INSERT INTO users (email, password_hash) VALUES (:e, 'x') RETURNING id"),
                {"e": f"rls-test-{tag}-{name}@example.com"},
            ).scalar_one()
            bid = c.execute(
                text(
                    "INSERT INTO businesses (user_id, jenis_usaha, lama_usaha_bulan, "
                    "jumlah_karyawan, nib_status, rekening_terpisah) "
                    "VALUES (:u, 'kuliner', 12, 1, 'belum', false) RETURNING id"
                ),
                {"u": uid},
            ).scalar_one()
            acc = c.execute(
                text(
                    "INSERT INTO accounts (business_id, name, kind) "
                    "VALUES (:b, 'Kas', 'kas') RETURNING id"
                ),
                {"b": bid},
            ).scalar_one()
            for _ in range(2):
                c.execute(
                    text(
                        "INSERT INTO transactions (business_id, account_id, type, amount, "
                        "occurred_on, source, client_uuid) VALUES "
                        "(:b, :a, 'sale', 1000, current_date, 'quick_sale', gen_random_uuid())"
                    ),
                    {"b": bid, "a": acc},
                )
            data[name] = {"user": uid, "business": bid, "account": acc}
    yield data
    with eng.begin() as c:
        c.execute(text("DELETE FROM users WHERE email LIKE :p"), {"p": f"rls-test-{tag}-%"})
    eng.dispose()


@pytest.fixture
def sm():
    engine = create_async_engine(get_settings().app_database_url, poolclass=NullPool)
    return async_sessionmaker(engine, expire_on_commit=False)


async def test_tenant_hanya_melihat_data_sendiri(seeded, sm):
    async with tenant_session(seeded["a"]["business"], sm) as s:
        rows = (await s.execute(text("SELECT business_id FROM transactions"))).all()
    assert len(rows) == 2
    assert {r[0] for r in rows} == {seeded["a"]["business"]}


async def test_tanpa_konteks_tidak_ada_baris(seeded, sm):
    async with plain_session(sm) as s:
        n = (await s.execute(text("SELECT count(*) FROM transactions"))).scalar_one()
    assert n == 0


async def test_insert_ke_usaha_lain_ditolak(seeded, sm):
    a, b = seeded["a"], seeded["b"]
    with pytest.raises(DBAPIError):
        async with tenant_session(a["business"], sm) as s:
            await s.execute(
                text(
                    "INSERT INTO transactions (business_id, account_id, type, amount, "
                    "occurred_on, source, client_uuid) VALUES "
                    "(:b, :a, 'sale', 5, current_date, 'manual', gen_random_uuid())"
                ),
                {"b": b["business"], "a": b["account"]},
            )


async def test_consents_append_only(seeded, sm):
    async with plain_session(sm) as s:
        await s.execute(
            text(
                "INSERT INTO consents (user_id, type, version, granted) "
                "VALUES (:u, 'financial_processing', 'v1', true)"
            ),
            {"u": seeded["a"]["user"]},
        )
    with pytest.raises(DBAPIError):
        async with plain_session(sm) as s:
            await s.execute(text("UPDATE consents SET granted = false"))


async def test_client_uuid_idempoten(seeded, sm):
    a = seeded["a"]
    cu = uuid.uuid4()
    sql = text(
        "INSERT INTO transactions (business_id, account_id, type, amount, occurred_on, "
        "source, client_uuid) VALUES (:b, :a, 'sale', 7, current_date, 'quick_sale', :cu)"
    )
    params = {"b": a["business"], "a": a["account"], "cu": cu}
    async with tenant_session(a["business"], sm) as s:
        await s.execute(sql, params)
    with pytest.raises(IntegrityError):
        async with tenant_session(a["business"], sm) as s:
            await s.execute(sql, params)
