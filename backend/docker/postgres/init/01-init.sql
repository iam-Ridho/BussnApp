-- Dijalankan sekali oleh container Postgres (dan oleh CI).
-- Role runtime: bukan superuser, bukan pemilik tabel, tidak bisa melewati RLS.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'bussn_app') THEN
    CREATE ROLE bussn_app LOGIN PASSWORD 'bussn_app_dev' NOSUPERUSER NOBYPASSRLS;
  END IF;
END $$;

GRANT CONNECT ON DATABASE bussnapp TO bussn_app;
