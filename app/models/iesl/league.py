from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import DatabaseModel, SlugKey

if TYPE_CHECKING:
    from .schedule import Schedule
    from .season import Season
    from .team import Team

__all__ = ["League"]


class Category(str, Enum):
    """League categories."""

    MEN = "Men's"
    WOMEN = "Women's"
    COED = "Coed"


class Division(str, Enum):
    """League divisions."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"


class MatchDay(str, Enum):
    """Day of week."""

    MON = "Monday"
    TUE = "Tuesday"
    WED = "Wednesday"
    THU = "Thursday"
    FRI = "Friday"
    SAT = "Saturday"
    SUN = "Sunday"


class League(DatabaseModel, SlugKey):
    """Inland Empire Soccer League.

    Args:
        name (str): League name
        category (Category): League category
        team_size (int): Team size
        division (Division): League division
        day_of_week (DayOfWeek): Day of week
        male_age_over (int): Male age over
        female_age_over (int): Female age over
    """

    __table_args__ = {"comment": "Inland Empire Soccer League"}

    season_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("season.id", ondelete="CASCADE"),
    )

    name: Mapped[str] = mapped_column(String(length=100), unique=True)
    category: Mapped[Category] = mapped_column(String(length=10))
    team_size: Mapped[int] = mapped_column(Integer())
    division: Mapped[Division] = mapped_column(String(length=4))
    day_of_week: Mapped[MatchDay] = mapped_column(String(length=10))
    male_age_over: Mapped[int] = mapped_column(Integer(), default=0)
    female_age_over: Mapped[int] = mapped_column(Integer(), default=0)

    # ORM
    season: Mapped["Season"] = relationship(back_populates="leagues")
    season_name: AssociationProxy[str] = association_proxy("season", "name")
    # home_team: Mapped["Team"] = relationship(back_populates="league")
    # away_team: Mapped["Team"] = relationship(back_populates="league")
    schedule: Mapped["Schedule"] = relationship(back_populates="league")
    teams: Mapped["Team"] = relationship(back_populates="league")
