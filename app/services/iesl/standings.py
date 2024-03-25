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
