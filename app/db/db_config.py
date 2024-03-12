import logging

from pydantic import PostgresDsn

from app.core import get_app_settings

logger = logging.getLogger(__name__)

settings = get_app_settings()

logger.info(f"Database URI: {settings.DATABASE_URI}")


def _is_sqlite(uri: str | None) -> bool:
    if uri is None:
        return False
    return "sqlite" in uri.lower()


def _create_str_uri() -> str:
    if not _is_sqlite(settings.DATABASE_URI):
        _postgres_uri = PostgresDsn.build(
            scheme="postgresql",
            username=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            path=f"/{settings.POSTGRES_DB_NAME}",
        )
        return str(_postgres_uri)
    if not settings.DATABASE_URI:
        raise ValueError("DATABASE_URI is not set")
    return settings.DATABASE_URI


def get_uri() -> str:
    return _create_str_uri()
