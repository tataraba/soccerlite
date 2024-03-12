from contextlib import asynccontextmanager

from advanced_alchemy.extensions.litestar.plugins import (
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
    SQLAlchemyPlugin,
)
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import (
    autocommit_before_send_handler,
)
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core import get_app_settings

from .db_config import get_uri

__all__ = ["get_async_session", "async_session_factory", "config", "plugin"]

settings = get_app_settings()

settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

engine = create_async_engine(
    url=get_uri(),
    echo=settings.DATABASE_ECHO,
    connect_args=settings.DATABASE_CONNECTION_ARGS,
)

async_session_factory = async_sessionmaker(engine, expire_on_commit=False)

config = SQLAlchemyAsyncConfig(
    engine_instance=engine,
    session_maker=async_session_factory,
    before_send_handler=autocommit_before_send_handler,
)

plugin = SQLAlchemyInitPlugin(config=config)


@asynccontextmanager
async def get_async_session():
    async with async_session_factory() as session:
        yield session
