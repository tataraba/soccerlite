from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import TYPE_CHECKING

from app.models.base import DatabaseModel

if TYPE_CHECKING:
    from .schedule import Schedule
    from .team import Team


__all__ = ["Standings"]


class Standings(DatabaseModel):

    __table_args__ = {"comment": "Inland Empire Scores League Standings"}

    schedule_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("schedule.id", ondelete="cascade"),
    )
    team_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("team.id", ondelete="set null"),
    )
    season: Mapped[String] = mapped_column(String(length=100), default="")
    games_played: Mapped[int] = mapped_column(Integer(), default=0)
    games_won: Mapped[int] = mapped_column(Integer(), default=0)
    games_drawn: Mapped[int] = mapped_column(Integer(), default=0)
    games_lost: Mapped[int] = mapped_column(Integer(), default=0)
    goals_for: Mapped[int] = mapped_column(Integer(), default=0)
    goals_against: Mapped[int] = mapped_column(Integer(), default=0)
    goals_difference: Mapped[int] = mapped_column(Integer(), default=0)
    points: Mapped[int] = mapped_column(Integer(), default=0)

    # ORM

    schedule: Mapped["Schedule"] = relationship(back_populates="standings")
    teams: Mapped[list["Team"]] = relationship(back_populates="standings")
