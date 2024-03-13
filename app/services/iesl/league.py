from typing import Any

from advanced_alchemy import FilterTypes
from sqlalchemy import select

from app import models
from app.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemyAsyncSlugRepository,
)

__all__ = [
    "LeagueRepo",
    "LeagueService",
]


class LeagueRepo(SQLAlchemyAsyncSlugRepository[models.League]):
    model_type = models.League

    async def list_without_season(
        self,
        *filters: FilterTypes,
        **kwargs: Any,
    ) -> list[models.League]:
        return await self.list(
            *filters,
            statement=select(models.League).filter(
                models.League.season == None
            ),  # noqa: E711
        )

    async def list_without_schedule(
        self,
        *filters: FilterTypes,
        **kwargs: Any,
    ) -> list[models.League]:
        return await self.list(
            *filters,
            statement=select(models.League).filter(
                models.League.schedule == None
            ),  # noqa: E711
        )


class LeagueService(SQLAlchemyAsyncRepositoryService[models.League]):
    repository_type = LeagueRepo

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: LeagueRepo = self.repository_type(**repo_kwargs)

    async def create(
        self,
        data: models.League | dict[str, Any],
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> models.League:
        """Create a new models. League with a slug."""

        db_obj = await self.to_model(data, "create")

        return await super().create(
            data=db_obj,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    async def to_model(
        self, data: models.League | dict[str, Any], operation: str | None = None
    ) -> models.League:
        data = await self.repository.include_slug_in_data(data)
        return await super().to_model(data, operation)
