from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import League

__all__ = ["LeagueDTO", "LeagueReadDTO", "LeagueCreateDTO", "LeagueUpdateDTO"]


class LeagueDTO(SQLAlchemyDTO[League]):
    pass


class LeagueReadDTO(SQLAlchemyDTO[League]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
        }
    )


class LeagueCreateDTO(SQLAlchemyDTO[League]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "season",
            "teams",
            "schedule",
            "slug",
        }
    )


class LeagueUpdateDTO(SQLAlchemyDTO[League]):
    config = SQLAlchemyDTOConfig(
        partial=True,
    )
