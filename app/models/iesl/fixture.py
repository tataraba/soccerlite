from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import UUID as UUIDType
from typing_extensions import TYPE_CHECKING

from app.models.base import DatabaseModel

if TYPE_CHECKING:
    from .fixture_team import FixtureTeam
    from .schedule import Schedule
    from .team import Team

__all__ = ["Fixture", "Field", "FixtureStatus"]


class Field(int, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8


class FixtureStatus(str, Enum):
    PLAYED = "Played"
    UNPLAYED = "Unplayed"
    FORFEIT = "Forfeit"
    ABANDONED = "Abandoned"
    POSTPONED = "Postponed"


class Fixture(DatabaseModel):
    """Inland Empire Scores League Fixture."""

    __table_args__ = {"comment": "Inland Empire Scores League Fixture"}

    schedule_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("schedule.id", ondelete="cascade"),
    )
    # team_home: Mapped[UUID | None] = mapped_column(
    #     ForeignKey("team.id", ondelete="set null"),
    # )
    # team_away: Mapped[UUID | None] = mapped_column(
    #     ForeignKey("team.id", ondelete="set null"),
    # )

    team_home_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True), nullable=False
    )
    team_away_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True), nullable=False
    )

    matchday: Mapped[int] = mapped_column(Integer())
    game_date: Mapped[datetime] = mapped_column(DateTime(), nullable=False)
    field: Mapped[Field] = mapped_column(Integer())
    referee_a: Mapped[str | None] = mapped_column(String(length=100), default="")
    referee_b: Mapped[str | None] = mapped_column(String(length=100), default="")
    team_home_goals: Mapped[int | None] = mapped_column(Integer(), default="")
    team_away_goals: Mapped[int | None] = mapped_column(Integer(), default="")
    mvp: Mapped[str | None] = mapped_column(String(length=50), default="")
    game_status: Mapped[FixtureStatus] = mapped_column(
        String(length=20), default=FixtureStatus.UNPLAYED
    )

    # ORM

    schedule: Mapped["Schedule"] = relationship(back_populates="fixtures")
    fixture_teams: Mapped[list["FixtureTeam"]] = relationship(
        back_populates="fixture", lazy="selectin", uselist=True, cascade="all, delete"
    )
    team_names: AssociationProxy[str] = association_proxy("fixture_teams", "team_name")
    # teams: Mapped["Team"] = relationship()
    # team_home_model: Mapped["Team"] = relationship("Team", foreign_keys=[team_home_id])
    # team_away_model: Mapped["Team"] = relationship("Team", foreign_keys=[team_away_id])
    # team_home_name: AssociationProxy[str] = AssociationProxy("team_home_model", "name")
    # team_away_name: AssociationProxy[str] = AssociationProxy("team_away_model", "name")
    team_home: Mapped["Team"] = relationship(
        "Team",
        primaryjoin="Team.id == Fixture.team_home_id",
        back_populates="home_team_fixtures",
        lazy="selectin",
        foreign_keys=[team_home_id],
    )
    team_away: Mapped["Team"] = relationship(
        "Team",
        primaryjoin="Team.id == Fixture.team_away_id",
        back_populates="away_team_fixtures",
        lazy="selectin",
        foreign_keys=[team_away_id],
    )
