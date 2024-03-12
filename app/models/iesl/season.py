from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime
from typing_extensions import TYPE_CHECKING

from app.models.base import DatabaseModel, SlugKey

if TYPE_CHECKING:
    from .league import League
    from .schedule import Schedule


__all__ = ["Season"]


class Season(DatabaseModel, SlugKey):
    """Inland Empire Soccer League Season is the parent model of the
    League models (children). It defines the parameters of each season."""

    __table_args__ = {"comment": "Inland Empire Scores League Season"}

    name: Mapped[str] = mapped_column(String(length=100), unique=True)
    description: Mapped[str | None] = mapped_column(String(length=120))
    start_date: Mapped[datetime.datetime] = mapped_column(DateTime())
    end_date: Mapped[Optional[datetime.datetime]] = mapped_column(default=None)
    active: Mapped[bool] = mapped_column(default=True)

    # ORM
    leagues: Mapped[list["League"]] = relationship(back_populates="season")
    schedule: Mapped["Schedule"] = relationship(back_populates="season")
