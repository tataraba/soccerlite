from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Fixture

__all__ = ["FixtureDTO", "FixtureReadDTO", "FixtureCreateDTO", "FixtureUpdateDTO"]


class FixtureDTO(SQLAlchemyDTO[Fixture]):
    pass


class FixtureReadDTO(SQLAlchemyDTO[Fixture]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
        }
    )


class FixtureCreateDTO(SQLAlchemyDTO[Fixture]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "slug",
            "schedule",
            "teams",
            "winning_team",
        }
    )


class FixtureUpdateDTO(SQLAlchemyDTO[Fixture]):
    config = SQLAlchemyDTOConfig(
        partial=True,
    )
