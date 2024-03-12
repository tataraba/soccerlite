from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from app import models
from app.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemyAsyncSlugRepository,
)

__all__ = [
    "TeamRepo",
    "TeamService",
]


class TeamRepo(SQLAlchemyAsyncSlugRepository[models.Team]):
    model_type = models.Team

    async def list_from_league(
        self,
        *filters: FilterTypes,
        league_id: UUID,
        **kwargs: Any,
    ):
        return await self.list(
            *filters,
            statement=select(models.Team).where(models.Team.league_id == league_id),
            **kwargs,
        )


class TeamService(SQLAlchemyAsyncRepositoryService[models.Team]):
    repository_type = TeamRepo

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: TeamRepo = self.repository_type(**repo_kwargs)

    async def list_from_league(
        self,
        *filters: FilterTypes,
        league_id: UUID,
        **kwargs: Any,
    ):
        return await self.repository.list_from_league(
            *filters, league_id=league_id, **kwargs
        )

    async def create(
        self,
        data: models.Team | dict[str, Any],
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> models.Team:
        """Create a new models. Team with a slug."""

        db_obj = await self.to_model(data, "create")

        return await super().create(
            data=db_obj,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    async def to_model(
        self, data: models.Team | dict[str, Any], operation: str | None = None
    ) -> models.Team:
        data = await self.repository.include_slug_in_data(data)
        return await super().to_model(data, operation)
