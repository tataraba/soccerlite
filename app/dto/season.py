from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models import Season

__all__ = ["SeasonDTO", "SeasonReadDTO", "SeasonCreateDTO", "SeasonUpdateDTO"]


class SeasonDTO(SQLAlchemyDTO[Season]):
    pass


class SeasonReadDTO(SQLAlchemyDTO[Season]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
        }
    )


class SeasonCreateDTO(SQLAlchemyDTO[Season]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "id",
            "end_date",
            "leagues",
            "schedule",
            "slug",
        }
    )


class SeasonUpdateDTO(SQLAlchemyDTO[Season]):
    config = SQLAlchemyDTOConfig(
        partial=True,
        exclude={
            "leagues",
        },
    )
