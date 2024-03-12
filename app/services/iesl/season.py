from typing import Any
from uuid import UUID

from advanced_alchemy import FilterTypes
from sqlalchemy import select
from sqlalchemy.orm import joinedload, noload, selectinload

from app import models
from app.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemyAsyncSlugRepository,
)

__all__ = [
    "SeasonRepo",
    "SeasonService",
]


class SeasonRepo(SQLAlchemyAsyncSlugRepository[models.Season]):
    model_type = models.Season

    async def get_season_leagues(
        self,
        *filters: FilterTypes,
        season_id: UUID,
        **kwargs: Any,
    ):
        """Get all leagues for a season."""
        statement = (
            select(models.League)
            .join_from(models.Season, models.League)
            .where(models.Season.id == season_id)
        )

        return await self.list_and_count(*filters, statement=statement, **kwargs)  # type: ignore


class SeasonService(SQLAlchemyAsyncRepositoryService[models.Season]):
    repository_type = SeasonRepo
    # match_fields = ["name"]

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: SeasonRepo = self.repository_type(**repo_kwargs)

    async def get_season_leagues(
        self,
        *filters: FilterTypes,
        season_id: UUID,
        **kwargs: Any,
    ):
        """Get all leagues for a season."""
        return await self.repository.get_season_leagues(
            *filters, season_id=season_id, **kwargs
        )

    async def create(
        self,
        data: models.Season | dict[str, Any],
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> models.Season:
        """Create a new models.Season with a slug."""

        db_obj = await self.to_model(data, "create")

        return await super().create(
            data=db_obj,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    async def to_model(
        self, data: models.Season | dict[str, Any], operation: str | None = None
    ) -> models.Season:
        data = await self.repository.include_slug_in_data(data)
        return await super().to_model(data, operation)
