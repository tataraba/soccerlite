from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.models import League, Schedule
from app.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemyAsyncSlugRepository,
)

__all__ = [
    "ScheduleRepo",
    "ScheduleService",
]


class ScheduleRepo(SQLAlchemyAsyncSlugRepository[Schedule]):
    model_type = Schedule

    async def get_schedule_for_league(self, league_id: UUID) -> Schedule:
        """
        Given a league_id select the corresponding League name from the
        League model.
        """
        statement = select(Schedule).where(Schedule.league_id == league_id)
        result = await self.session.execute(statement=statement)
        schedule = result.scalars().first()
        if schedule is None:
            raise ValueError(f"Couldn't find league name for {self.model_type}.")
        return schedule

    async def get_league(self, league_id: UUID) -> League:
        """
        Given a league_id from the Schedule model, select the
        corresponding League name from the League model.
        """
        statement = select(League).where(League.id == league_id)
        result = await self.session.execute(statement=statement)
        league = result.scalar_one_or_none()
        if league is None:
            raise ValueError(f"Couldn't find league name for {self.model_type}.")
        return league


class ScheduleService(SQLAlchemyAsyncRepositoryService[Schedule]):
    repository_type = ScheduleRepo

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: ScheduleRepo = self.repository_type(**repo_kwargs)

    async def get_schedule_for_league(self, league_id: UUID) -> Schedule:
        return await self.repository.get_schedule_for_league(league_id)

    async def get_league_name(self, league_id: UUID) -> Schedule:
        return await self.repository.get_schedule_for_league(league_id)

    async def create(
        self,
        data: Schedule | dict[str, Any],
        auto_commit: bool | None = None,
        auto_expunge: bool | None = None,
        auto_refresh: bool | None = None,
    ) -> Schedule:
        """Create a new models. Schedule with a slug."""

        db_obj = await self.to_model(data, "create")

        return await super().create(
            data=db_obj,
            auto_commit=auto_commit,
            auto_expunge=auto_expunge,
            auto_refresh=auto_refresh,
        )

    async def to_model(
        self, data: Schedule | dict[str, Any], operation: str | None = None
    ) -> Schedule:
        if isinstance(data, Schedule):
            league = await self.repository.get_league(data.league_id)
            data = data.to_dict()
            data["name"] = f"{league.name} schedule"  # field that is slugified
        data = await self.repository.include_slug_in_data(data)
        return await super().to_model(data, operation)
