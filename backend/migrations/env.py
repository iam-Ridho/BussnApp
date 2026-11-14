from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import get_settings

target_metadata = None  # migrasi ditulis sebagai SQL eksplisit, bukan autogenerate


def run_migrations_online() -> None:
    engine = create_engine(get_settings().migrator_database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
