from __future__ import annotations

from enum import Enum
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import TYPE_CHECKING

from app.models.base import DatabaseModel

if TYPE_CHECKING:
    from .fixture import Fixture
    from .team import Team


__all__ = ["FixtureTeam"]


class FixtureResult(str, Enum):
    W = "Win"
    D = "Draw"
    L = "Loss"


class FixtureTeam(DatabaseModel):
    """Association table between teams and fixtures."""

    __table_args__ = (UniqueConstraint("team_id", "fixture_id"),)

    team_id: Mapped[UUID] = mapped_column(
        ForeignKey("team.id", ondelete="cascade"), nullable=False
    )
    fixture_id: Mapped[UUID] = mapped_column(
        ForeignKey("fixture.id", ondelete="cascade"), nullable=False
    )
    is_played: Mapped[bool] = mapped_column(default=False)
    result: Mapped[FixtureResult] = mapped_column(default=FixtureResult.D)
    points: Mapped[int] = mapped_column(default=0)
    goals_for: Mapped[int] = mapped_column(default=0)
    goals_against: Mapped[int] = mapped_column(default=0)

    # ORM
    team: Mapped["Team"] = relationship(
        back_populates="fixtures",
        foreign_keys="FixtureTeam.team_id",
        innerjoin=True,
        lazy="joined",
    )
    team_name: AssociationProxy[str] = association_proxy("team", "name")
    team_contact: AssociationProxy[str] = association_proxy("team", "contact_name")
    fixture: Mapped["Fixture"] = relationship(
        back_populates="fixture_teams",
        foreign_keys="FixtureTeam.fixture_id",
        innerjoin=True,
        lazy="joined",
    )
    fixture_team_home: AssociationProxy[bool] = association_proxy(
        "fixture", "team_home"
    )
    fixture_away_team: AssociationProxy[bool] = association_proxy(
        "fixture", "team_away"
    )
    fixture_matchday: AssociationProxy[int] = association_proxy("fixture", "matchday")
