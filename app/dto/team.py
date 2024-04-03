from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Team

__all__ = ["TeamDTO", "TeamReadDTO", "TeamCreateDTO", "TeamUpdateDTO"]


class TeamDTO(SQLAlchemyDTO[Team]):
    pass


class TeamReadDTO(SQLAlchemyDTO[Team]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
        }
    )


class TeamCreateDTO(SQLAlchemyDTO[Team]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "slug",
            "league",
            "fixtures",
            "standings",
            "home_team_fixtures",
            "away_team_fixtures",
        }
    )


class TeamUpdateDTO(SQLAlchemyDTO[Team]):
    config = SQLAlchemyDTOConfig(
        partial=True,
    )
