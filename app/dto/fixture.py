from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DataclassDTO, DTOConfig

from app.models import Fixture

__all__ = ["FixtureDTO", "FixtureReadDTO", "FixtureCreateDTO", "FixtureUpdateDTO"]


class FixtureDTO(SQLAlchemyDTO[Fixture]):
    pass


class FixtureReadDTO(SQLAlchemyDTO[Fixture]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
        }
    )


class FixtureCreateDTO(SQLAlchemyDTO[Fixture]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "slug",
            "schedule",
            "teams",
            "winning_team",
        }
    )


class FixtureUpdateDTO(SQLAlchemyDTO[Fixture]):
    config = SQLAlchemyDTOConfig(
        partial=True,
    )


@dataclass
class FixtureSchedule:
    schedule_id: UUID
    team_home_id: UUID
    team_away_id: UUID
    team_home_name: str
    team_away_name: str
    matchday: int
    game_date: datetime
    field: int
    referee_a: str
    referee_b: str
    team_home_goals: int
    team_away_goals: int
    mvp: str
    game_status: str


class FixtureScheduleDTO(DataclassDTO[FixtureSchedule]):
    ...
