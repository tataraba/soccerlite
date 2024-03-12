from dataclasses import dataclass

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DataclassDTO

from app.models import Roles, UserLoginData


@dataclass
class UserRegistrationSchema:
    email: str
    password: str


class UserRegistrationDTO(DataclassDTO[UserRegistrationSchema]):
    """User registration DTO."""

    pass


class UserReadDTO(SQLAlchemyDTO[UserLoginData]):
    config = SQLAlchemyDTOConfig(exclude={"login_count"})


class UserUpdateDTO(SQLAlchemyDTO[UserLoginData]):
    config = SQLAlchemyDTOConfig(exclude={"login_count"}, partial=True)


class RoleCreateDTO(SQLAlchemyDTO[Roles]):
    config = SQLAlchemyDTOConfig(exclude={"id", "created_at", "updated_at"})


class RoleReadDTO(SQLAlchemyDTO[Roles]):
    pass


class RoleUpdateDTO(SQLAlchemyDTO[Roles]):
    config = SQLAlchemyDTOConfig(
        exclude={"id", "created_at", "updated_at"}, partial=True
    )
