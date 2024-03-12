from enum import Enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models import base

__all__ = ["Roles", "Permissions", "RolesPermissionsLink"]


class RoleTypes(str, Enum):
    """User Roles."""

    GUEST = "GUEST"
    ADMIN = "ADMIN"
    USER = "USER"
    CAPTAIN = "CAPTAIN"


class Roles(base.DatabaseModel, base.AuditColumns):
    """User Account details."""

    __table_args__ = {"comment": "Inland Empire Soccer League"}

    name: Mapped[RoleTypes] = mapped_column(String(length=10), default=RoleTypes.GUEST)
    description: Mapped[str] = mapped_column(
        String(length=120),
    )


class Permissions(base.DatabaseModel, base.AuditColumns):
    """User Account details."""

    __table_args__ = {"comment": "Inland Empire Scores League"}

    description: Mapped[str] = mapped_column(
        String(length=50),
    )


class RolesPermissionsLink(base.DatabaseModel, base.AuditColumns):
    """User Account details."""

    __table_args__ = {"comment": "Inland Empire Scores League"}

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="cascade"))
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="cascade")
    )
