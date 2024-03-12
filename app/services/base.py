"""Base SQLAlchemy Repository pattern.
Reference: https://github.com/cofin/litestar-fullstack/blob/react-vite-litestar/src/app/lib/repository.py
"""

import contextlib
import random
import string
from collections.abc import AsyncIterator
from typing import Any, TypeVar

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.repository.typing import ModelT
from advanced_alchemy.service import (
    SQLAlchemyAsyncRepositoryService as _SQLAlchemyAsyncRepositoryService,
)
from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.toolbox import slugify
from app.models.base import DatabaseModel

__all__ = ["SQLAlchemyAsyncRepository", "SQLAlchemyAsyncSlugRepository"]

SQLAlchemyAsyncRepoServiceT = TypeVar(
    "SQLAlchemyAsyncRepoServiceT", bound="SQLAlchemyAsyncRepositoryService"
)
DatabaseModelT = TypeVar("DatabaseModelT", bound=DatabaseModel)


class SQLAlchemyAsyncSlugRepository(
    SQLAlchemyAsyncRepository[ModelT],
):
    """Extends the repository to include slug model features.."""

    async def get_by_slug(
        self,
        slug: str,
        **kwargs: Any,
    ) -> ModelT | None:
        """Select record by slug value."""
        return await self.get_one_or_none(slug=slug)

    async def get_available_slug(
        self,
        value_to_slugify: str,
        **kwargs: Any,
    ) -> str:
        """Get a unique slug for the supplied value.

        If the value is found to exist, a random 4 digit character is appended to the end.
        There may be a better way to do this, but I wanted to limit the number of additional database
        calls.

        Args:
            value_to_slugify (str): A string that should be converted to a unique slug.
            **kwargs: stuff

        Returns:
            str: a unique slug for the supplied value.  This is safe for URLs and other unique identifiers.
        """
        slug = slugify(value_to_slugify)
        if await self._is_slug_unique(slug):
            return slug
        random_string = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=4)
        )  # noqa: S311
        return f"{slug}-{random_string}"

    async def _is_slug_unique(
        self,
        slug: str,
        **kwargs: Any,
    ) -> bool:
        return await self.exists(slug=slug) is False

    async def include_slug_in_data(self, data: DatabaseModelT | dict[str, Any]) -> dict:
        """Given a `DatabaseMode` or a `dict`, check if it has a `slug` and if not, add one.

        Args:
            data (DatabaseModelT | dict[str, Any]): A `DatabaseModel` or a `dict`.

        Returns:
            dict: A `dict` with a `slug` key if it exists or was added.
        """
        if isinstance(data, DatabaseModel):
            data = data.to_dict()
        if "slug" not in data:
            data["slug"] = await self.get_available_slug(data["name"])
        return data


class SQLAlchemyAsyncRepositoryService(_SQLAlchemyAsyncRepositoryService[ModelT]):
    @classmethod
    @contextlib.asynccontextmanager
    async def new(
        cls: type[SQLAlchemyAsyncRepoServiceT],
        session: AsyncSession | None = None,
        statement: Select | None = None,
    ) -> AsyncIterator[SQLAlchemyAsyncRepoServiceT]:
        from app.db import async_session_factory

        if session:
            yield cls(statement=statement, session=session)
        else:
            async with async_session_factory() as db_session:
                yield cls(
                    statement=statement,
                    session=db_session,
                )
