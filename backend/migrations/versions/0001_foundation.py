"""Fondasi: akun, usaha, setup awal, transaksi, scoring_config, RLS

Revision ID: 0001
Revises:
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

TENANT_TABLES = {  # tabel -> kolom penentu usaha
    "businesses": "id",
    "accounts": "business_id",
    "setup_assets": "business_id",
    "setup_debts": "business_id",
    "transactions": "business_id",
}
UPDATED_AT_TABLES = [
    "users",
    "businesses",
    "accounts",
    "setup_assets",
    "setup_debts",
    "transactions",
]

# CATATAN: op.execute() memakai text(); ":nama" dibaca sebagai bind parameter.
# Titik dua literal (mis. di JSON) harus ditulis \\: dan jangan taruh ":kata" di komentar SQL.
SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END $$ LANGUAGE plpgsql;

CREATE TABLE users (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email         text NOT NULL,
  password_hash text NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  deleted_at    timestamptz
);
CREATE UNIQUE INDEX users_email_lower_uq ON users (lower(email));

-- Riwayat persetujuan: append-only (role aplikasi tidak diberi UPDATE/DELETE)
CREATE TABLE consents (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type       text NOT NULL CHECK (type IN ('financial_processing', 'ai_processing')),
  version    text NOT NULL,
  granted    boolean NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX consents_user_idx ON consents (user_id, type, created_at DESC);

CREATE TABLE refresh_tokens (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash text NOT NULL UNIQUE,
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE businesses (
  id                 uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id            uuid NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  name               text,
  jenis_usaha        text NOT NULL,
  lama_usaha_bulan   integer NOT NULL CHECK (lama_usaha_bulan >= 0),
  jumlah_karyawan    integer NOT NULL CHECK (jumlah_karyawan >= 0),
  nib_status         text NOT NULL CHECK (nib_status IN ('punya', 'proses', 'belum')),
  rekening_terpisah  boolean NOT NULL,
  modal_awal         bigint NOT NULL DEFAULT 0 CHECK (modal_awal >= 0),
  setup_complete     boolean NOT NULL DEFAULT false,
  timezone           text NOT NULL DEFAULT 'Asia/Makassar',
  data_version       bigint NOT NULL DEFAULT 0,
  created_at         timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE accounts (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id     uuid NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  name            text NOT NULL,
  kind            text NOT NULL CHECK (kind IN ('kas', 'rekening', 'qris')),
  is_business     boolean NOT NULL DEFAULT true,
  opening_balance bigint NOT NULL DEFAULT 0,
  created_at      timestamptz NOT NULL DEFAULT now(),
  updated_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX accounts_business_idx ON accounts (business_id);

CREATE TABLE setup_assets (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id uuid NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  name        text NOT NULL,
  value       bigint NOT NULL CHECK (value >= 0),
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX setup_assets_business_idx ON setup_assets (business_id);

CREATE TABLE setup_debts (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id         uuid NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  creditor            text NOT NULL,
  remaining           bigint NOT NULL CHECK (remaining >= 0),
  monthly_installment bigint NOT NULL DEFAULT 0 CHECK (monthly_installment >= 0),
  active              boolean NOT NULL DEFAULT true,
  created_at          timestamptz NOT NULL DEFAULT now(),
  updated_at          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX setup_debts_business_idx ON setup_debts (business_id);

CREATE TABLE categories (
  code     text PRIMARY KEY,
  name     text NOT NULL,
  kelompok text NOT NULL CHECK (kelompok IN ('hpp', 'operasional')),
  sifat    text NOT NULL CHECK (sifat IN ('tetap', 'variabel'))
);
INSERT INTO categories (code, name, kelompok, sifat) VALUES
  ('bahan_baku',         'Bahan baku',                   'hpp',         'variabel'),
  ('kemasan',            'Kemasan',                      'hpp',         'variabel'),
  ('tenaga_kerja',       'Gaji dan upah',                'operasional', 'tetap'),
  ('sewa',               'Sewa tempat',                  'operasional', 'tetap'),
  ('utilitas',           'Listrik, air, internet',       'operasional', 'tetap'),
  ('transport',          'Transportasi dan pengiriman',  'operasional', 'variabel'),
  ('pemasaran',          'Promosi dan pemasaran',        'operasional', 'variabel'),
  ('perawatan_alat',     'Perawatan peralatan',          'operasional', 'tetap'),
  ('administrasi_pajak', 'Administrasi, izin, pajak',    'operasional', 'tetap'),
  ('lainnya',            'Lainnya',                      'operasional', 'variabel');

-- receipt_id dan import_row_id belum punya FK: tabelnya dibuat di migrasi berikutnya.
CREATE TABLE transactions (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id   uuid NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
  account_id    uuid NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
  type          text NOT NULL CHECK (type IN
                  ('sale', 'expense', 'capital_in', 'asset_purchase', 'debt_payment')),
  category_code text REFERENCES categories(code),
  amount        bigint NOT NULL CHECK (amount > 0),
  occurred_on   date NOT NULL,
  tag           text NOT NULL DEFAULT 'usaha' CHECK (tag IN ('usaha', 'pribadi', 'belum_ditag')),
  source        text NOT NULL CHECK (source IN
                  ('receipt', 'bank_import', 'quick_sale', 'manual', 'daily_recap')),
  receipt_id    uuid,
  import_row_id uuid,
  client_uuid   uuid NOT NULL,
  note          varchar(200),
  deleted_at    timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT transactions_idempotency_uq UNIQUE (business_id, client_uuid)
);
CREATE INDEX transactions_business_date_idx ON transactions (business_id, occurred_on);
CREATE INDEX transactions_business_tag_idx  ON transactions (business_id, tag);

-- Bobot dari PRD 3.6. Indikator G, E, B dimatikan untuk MVP:
-- bobotnya dinormalkan ulang oleh Rule Engine (PRD 3.6).
CREATE TABLE scoring_config (
  key        text PRIMARY KEY,
  value      jsonb NOT NULL,
  version    integer NOT NULL DEFAULT 1,
  updated_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO scoring_config (key, value) VALUES
  ('weights',
   '{"P"\\:0.20,"C"\\:0.20,"G"\\:0.10,"E"\\:0.15,"D"\\:0.15,"B"\\:0.10,"A"\\:0.10}'),
  ('enabled',
   '{"P"\\:true,"C"\\:true,"D"\\:true,"A"\\:true,"G"\\:false,"E"\\:false,"B"\\:false}');
"""

RLS_SQL = """
ALTER TABLE {t} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {t} FORCE ROW LEVEL SECURITY;
-- nullif: setelah transaksi selesai, current_setting mengembalikan '' (bukan NULL).
-- Tanpa konteks usaha, perbandingan menjadi NULL sehingga tidak ada baris yang lolos.
CREATE POLICY tenant_isolation ON {t}
  USING      ({c} = nullif(current_setting('app.business_id', true), '')::uuid)
  WITH CHECK ({c} = nullif(current_setting('app.business_id', true), '')::uuid);
"""

GRANT_SQL = """
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'bussn_app') THEN
    GRANT USAGE ON SCHEMA public TO bussn_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bussn_app;
    REVOKE UPDATE, DELETE ON consents FROM bussn_app;        -- append-only (PDP-02)
    REVOKE INSERT, UPDATE, DELETE ON categories, scoring_config FROM bussn_app;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
      GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO bussn_app;
  END IF;
END $$;
"""


def upgrade() -> None:
    op.execute(SCHEMA_SQL)
    for t in UPDATED_AT_TABLES:
        op.execute(
            f"CREATE TRIGGER {t}_set_updated_at BEFORE UPDATE ON {t} "
            "FOR EACH ROW EXECUTE FUNCTION set_updated_at()"
        )
    for t, col in TENANT_TABLES.items():
        op.execute(RLS_SQL.format(t=t, c=col))
    op.execute(GRANT_SQL)


def downgrade() -> None:
    raise NotImplementedError("Migrasi hanya maju (PRD 7.3)")
