from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Schedule

__all__ = ["ScheduleDTO", "ScheduleReadDTO", "ScheduleCreateDTO", "ScheduleUpdateDTO"]


class ScheduleDTO(SQLAlchemyDTO[Schedule]):
    pass


class ScheduleReadDTO(SQLAlchemyDTO[Schedule]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
        }
    )


class ScheduleCreateDTO(SQLAlchemyDTO[Schedule]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "slug",
            "league",
            "season",
            "fixtures",
        }
    )


class ScheduleUpdateDTO(SQLAlchemyDTO[Schedule]):
    config = SQLAlchemyDTOConfig(
        partial=True,
        exclude={
            "id",
            "league_id",
            "season_id",
        },
    )
