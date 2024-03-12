"""Application ORM configuration.
Reference: https://github.com/litestar-org/litestar-fullstack/blob/main/src/app/lib/db/orm.py
"""

from __future__ import annotations

from advanced_alchemy.base import AuditColumns, orm_registry
from advanced_alchemy.base import UUIDAuditBase as TimestampedDatabaseModel
from advanced_alchemy.base import UUIDBase as DatabaseModel
from advanced_alchemy.repository import model_from_dict
from sqlalchemy import String
from sqlalchemy.orm import (
    Mapped,
    declarative_mixin,
    mapped_column,
)

__all__ = [
    "DatabaseModel",
    "TimestampedDatabaseModel",
    "orm_registry",
    "model_from_dict",
    "AuditColumns",
    "SlugKey",
]


@declarative_mixin
class SlugKey:
    """Slug unique Field Model Mixin."""

    __abstract__ = True
    slug: Mapped[str] = mapped_column(
        String(length=100), index=True, nullable=False, unique=True, sort_order=-9
    )
