from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import base

if TYPE_CHECKING:
    from . import Roles

__all__ = [
    "UserAccount",
    "UserLoginData",
]


class UserLoginData(base.TimestampedDatabaseModel, base.AuditColumns):
    """Details of user data for login."""

    __table_args__ = {"comment": "Contains user account data."}

    username: Mapped[str] = mapped_column(String(length=24), unique=True)
    email: Mapped[str] = mapped_column(String(length=100), unique=True)
    password_hash: Mapped[str] = mapped_column(String(length=250), nullable=False)
    password_salt: Mapped[str] = mapped_column(String(length=100), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    # TODO: Add DTOs private
    confirmation_token: Mapped[str | None] = mapped_column(String(length=100))
    token_expiry: Mapped[datetime | None] = mapped_column(
        String(length=10),
    )
    email_validation_status_id: Mapped[int] = mapped_column(
        String(length=1),
        default=0,
    )
    password_reset_token: Mapped[str | None] = mapped_column(String(length=100))
    password_reset_token_expiry: Mapped[datetime | None] = mapped_column(
        String(length=10),
    )

    # ORM
    roles: Mapped[list["Roles"]] = relationship(
        "Roles",
        secondary="user_role",
        lazy="selectin",
    )


class UserAccount(base.TimestampedDatabaseModel, base.AuditColumns):
    """User Account details."""

    __table_args__ = {"comment": "Account details with identity."}
    user_login_id: Mapped[UUID] = mapped_column(
        ForeignKey("user_login_data.id", ondelete="cascade")
    )
    first_name: Mapped[str] = mapped_column(String(length=100), unique=True)
    last_name: Mapped[str] = mapped_column(String(length=100), unique=True)
    date_of_birth: Mapped[datetime] = mapped_column(
        String(length=10),
    )


class UserRole(base.DatabaseModel):
    """User Account details."""

    __table_args__ = {"comment": "Inland Empire Scores League"}
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_login_data.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
