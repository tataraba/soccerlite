# see https://github.com/litestar-org/litestar-fullstack/blob/main/src/app/lib/db/utils.py
import logging

import anyio
from alembic import command as migration_command
from alembic.config import Config as AlembicConfig
from sqlalchemy import Table
from sqlalchemy.schema import DropTable

from app.core import get_app_settings
from app.models.base import DatabaseModel, orm_registry

from .base import engine

__all__ = [
    "create_database",
    "upgrade_database",
    "reset_database",
    "show_database_revision",
    "purge_database",
]

logger = logging.getLogger(__name__)
settings = get_app_settings()
migration_path: str = str(settings.ALEMBIC_MIGRATION_PATH)


def create_database() -> None:
    """Create database DDL migrations."""
    logger.info(f"Creating database: {settings.DATABASE_URI}")
    alembic_cfg = AlembicConfig(settings.ALEMBIC_CONFIG)
    alembic_cfg.set_main_option("script_location", migration_path)
    migration_command.upgrade(alembic_cfg, "head")


def upgrade_database() -> None:
    """Upgrade the database to the latest revision."""
    alembic_cfg = AlembicConfig(settings.ALEMBIC_CONFIG)
    alembic_cfg.set_main_option("script_location", migration_path)
    migration_command.upgrade(alembic_cfg, "head")


def reset_database() -> None:
    """Reset the database to an initial empty state."""
    alembic_cfg = AlembicConfig(settings.ALEMBIC_CONFIG)
    alembic_cfg.set_main_option("script_location", migration_path)
    anyio.run(drop_tables)  # type: ignore
    migration_command.upgrade(alembic_cfg, "head")


def purge_database() -> None:
    """Drop all objects in the database."""
    alembic_cfg = AlembicConfig(settings.ALEMBIC_CONFIG)
    alembic_cfg.set_main_option("script_location", migration_path)
    anyio.run(drop_tables)  # type: ignore


def show_database_revision() -> None:
    """Show current database revision."""
    alembic_cfg = AlembicConfig(settings.ALEMBIC_CONFIG)
    alembic_cfg.set_main_option("script_location", migration_path)
    migration_command.current(alembic_cfg, verbose=False)


async def drop_tables() -> None:
    """Drop all tables from the database."""
    logger.info("Connecting to database backend.")
    async with engine.begin() as db:
        logger.info("Dropping the db")
        await db.run_sync(DatabaseModel.metadata.drop_all)
        logger.info("Dropping the version table")

        await db.execute(
            DropTable(
                element=Table("ddl_version", orm_registry.metadata),
                if_exists=True,
            ),
        )
        await db.commit()
    logger.info("Successfully dropped all objects")
