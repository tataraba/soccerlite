from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import TYPE_CHECKING

from app.models.base import DatabaseModel, SlugKey

if TYPE_CHECKING:
    from .fixture import Fixture
    from .league import League
    from .season import Season
    from .standings import Standings

__all__ = ["Schedule"]


class Schedule(DatabaseModel, SlugKey):
    """Inland Empire Soccer League Schedule. Schedule is tied to a season and league
    and determines the structure of the fixtures.

    Args:
        league_id (UUID): ID of the league.
        season_id (UUID): ID of the season.
        scheduled_start (datetime): Determines date/time of first fixture.
        total_games (int): Total number of games in the schedule. Defaults to 10.
        time_between_games (int): Time between start of matches. Defaults to 60.
        concurrent_games (int): Determines if matches are played at the same time.
        published (bool): Whether the schedule is published to end users.

    """

    __table_args__ = (
        UniqueConstraint("league_id", "season_id", name="uq_league_season"),
    )

    league_id: Mapped[UUID] = mapped_column(
        ForeignKey("league.id", ondelete="cascade"),
    )
    season_id: Mapped[UUID] = mapped_column(
        ForeignKey("season.id", ondelete="cascade"),
    )
    scheduled_start: Mapped[datetime] = mapped_column(
        DateTime(), nullable=False, default=datetime.utcnow()
    )
    total_games: Mapped[int] = mapped_column(Integer(), default=10, nullable=False)
    time_between_games: Mapped[int] = mapped_column(Integer(), default=60)
    concurrent_games: Mapped[int] = mapped_column(Integer(), default=6)
    published: Mapped[bool] = mapped_column(default=False)

    # ORM

    league: Mapped["League"] = relationship(
        back_populates="schedule", innerjoin=True, uselist=False, lazy="joined"
    )
    league_name: AssociationProxy[str] = association_proxy("league", "name")
    league_slug: AssociationProxy[str] = association_proxy("league", "slug")
    season: Mapped["Season"] = relationship(
        back_populates="schedule", innerjoin=True, uselist=False, lazy="joined"
    )
    season_name: AssociationProxy[str] = association_proxy("season", "name")
    fixtures: Mapped[list["Fixture"]] = relationship(back_populates="schedule")
    standings: Mapped["Standings"] = relationship(back_populates="schedule")
