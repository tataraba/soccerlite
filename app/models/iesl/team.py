from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import TYPE_CHECKING

from app.models.base import DatabaseModel, SlugKey

from .fixture import Fixture

if TYPE_CHECKING:
    from .fixture_team import FixtureTeam
    from .league import League
    from .standings import Standings

__all__ = ["Team"]


class Team(DatabaseModel, SlugKey):
    """Inland Empire Soccer League Team."""

    __table_args__ = {"comment": "Team details"}

    league_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("league.id", ondelete="cascade"),
    )

    name: Mapped[str] = mapped_column(String(length=100), unique=True)
    uniform_color: Mapped[str] = mapped_column(String(length=100), default="")
    active: Mapped[bool] = mapped_column(default=True)
    contact_name: Mapped[str] = mapped_column(String(length=100), default="")
    contact_email: Mapped[str] = mapped_column(String(length=100), default="")
    contact_phone: Mapped[str] = mapped_column(String(length=100), default="")
    team_image: Mapped[str | None] = mapped_column(String(length=100), default="")
    team_logo: Mapped[str | None] = mapped_column(String(length=100), default="")

    # ORM
    fixtures: Mapped[list["FixtureTeam"]] = relationship(
        back_populates="team",
        cascade="all, delete",
        lazy="selectin",
    )
    league: Mapped["League"] = relationship(back_populates="teams")
    standings: Mapped["Standings"] = relationship(back_populates="team")
    # players: Mapped[list["PlayerTeamLink"]] = relationship(back_populates="team")
    home_team_fixtures: Mapped[list["Fixture"]] = relationship(
        primaryjoin="Team.id == Fixture.team_home_id",
        back_populates="team_home",
        foreign_keys=[Fixture.team_home_id],
        lazy="selectin",
        uselist=True,
    )
    away_team_fixtures: Mapped[list["Fixture"]] = relationship(
        primaryjoin="Team.id == Fixture.team_away_id",
        back_populates="team_away",
        foreign_keys=[Fixture.team_away_id],
        lazy="selectin",
        uselist=True,
    )
