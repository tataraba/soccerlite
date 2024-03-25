from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Schedule


class StandingsDTO(SQLAlchemyDTO[Schedule]):
    pass


class StandingsReadDTO(SQLAlchemyDTO[Schedule]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
        }
    )


class StandingsCreateDTO(SQLAlchemyDTO[Schedule]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "slug",
        }
    )


class StandingsUpdateDTO(SQLAlchemyDTO[Schedule]):
    config = SQLAlchemyDTOConfig(
        partial=True,
        exclude={
            "id",
            "schedule_id",
            "season_id",
        },
    )
