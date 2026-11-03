"""
alembic/env.py — Alembic migration environment.

Reads the database URL from app.config.settings so the same .env-based
configuration used by the application also drives migrations.

Usage:
  Apply all pending migrations:
    alembic upgrade head

  Roll back the most recent migration:
    alembic downgrade -1

  Check current revision:
    alembic current

  Show pending migrations:
    alembic history --verbose
"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ── Import application models so Alembic can detect schema changes ────────────
# This import is what makes `alembic revision --autogenerate` work.
from app.database import Base
import app.models.db_models  # noqa: F401 — registers all ORM models with Base

# ── Read the database URL from application settings ───────────────────────────
from app.config import settings

# Alembic Config object — provides access to alembic.ini values.
config = context.config

# Override the sqlalchemy.url from our settings (ignores the blank value in
# alembic.ini).
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData from all registered models — required for --autogenerate.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Required for SQLite ALTER TABLE support.
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (live DB connection)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Required for SQLite ALTER TABLE support.
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
