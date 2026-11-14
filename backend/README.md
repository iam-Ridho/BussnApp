# Backend

FastAPI + PostgreSQL 16 + Redis. Semua perintah dijalankan dari folder `backend/`.

## Pertama kali
```
uv sync
copy .env.example .env        (Mac/Linux: cp .env.example .env)
docker compose up -d
uv run alembic upgrade head
uv run pytest -q              (harus: 18 passed)
uv run uvicorn app.main:app --reload --port 8000
```
Buka http://localhost:8000/docs

## Kontrak API
Setelah mengubah router atau skema, ekspor ulang kontrak (ada di root repo) lalu commit:
```
uv run python -m scripts.export_openapi
```

## Aturan penting
- Aplikasi berjalan sebagai role `bussn_app` (bukan pemilik tabel, RLS berlaku).
  `MIGRATOR_DATABASE_URL` hanya untuk Alembic; jangan dipakai di kode aplikasi.
- Tabel milik usaha hanya diakses lewat `tenant_session(business_id)` di `app/core/db.py`.
- Rule Engine (`app/rule_engine/`) Python murni: Decimal, tanpa float, tanpa akses DB.
- Migrasi hanya maju. `op.execute()` memakai text(): tulis `\\:` untuk titik dua literal
  dan jangan menaruh pola `:kata` di komentar SQL.
