from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.models import Fixture, Schedule, Standings
from app.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemyAsyncSlugRepository,
)

__all__ = [
    "StandingsRepo",
    "StandingsService",
]


class StandingsRepo(SQLAlchemyAsyncSlugRepository[Standings]):
    model_type = Standings


class StandingsService(SQLAlchemyAsyncRepositoryService[Standings]):
    repository_type = StandingsRepo

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: StandingsRepo = self.repository_type(**repo_kwargs)

    async def create(
        self,
        data: Standings | dict[str, Any],
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> Standings:
        """Create a new models. Schedule with a slug."""

        db_obj = await self.to_model(data, "create")

        return await super().create(
            data=db_obj,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    async def to_model(
        self, data: Standings | dict[str, Any], operation: str | None = None
    ) -> Standings:
        if isinstance(data, Standings):
            data = data.to_dict()
        data = await self.repository.include_slug_in_data(data)
        return await super().to_model(data, operation)
