from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated

from advanced_alchemy.exceptions import ConflictError, NotFoundError
from litestar import Controller, delete, get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.datastructures import CacheControlHeader
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect, Template

from app.controllers import urls
from app.core.response import htmx_template
from app.dto import SeasonCreateDTO, SeasonUpdateDTO
from app.models import Season
from app.services import (
    provide_league_repo,
    provide_season_repo,
    provide_season_service,
)
from app.services.iesl import LeagueRepo, SeasonRepo, SeasonService


class AdminSeasonController(Controller):
    guards = []
    cache_control = CacheControlHeader(
        no_cache=True, no_store=True, must_revalidate=True
    )

    @get(
        [urls.ADMIN_INDEX],
        status_code=HTTPStatus.OK,
        name="admin_index",
        dependencies={"season_service": provide_season_service},
    )
    async def admin_index(
        self, season_service: SeasonService, request: HTMXRequest
    ) -> Template:
        seasons = await season_service.list()
        return htmx_template(
            template_name="admin/dashboard.html",
            context={"seasons": seasons, "view": "tile_view"},
        )

    @get(
        [urls.ADMIN_SEASON],
        status_code=HTTPStatus.OK,
        name="get_seasons",
        dependencies={"season_service": provide_season_service},
    )
    async def get_seasons(
        self,
        season_service: SeasonService,
        request: HTMXRequest,
    ) -> Template:
        view_type = request.headers.get("view")
        if not view_type:
            view_type = "tile_view"
        seasons = await season_service.list()
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/season-index.html",
                context={"seasons": seasons, "view": view_type},
            )
        return htmx_template(
            template_name="admin/dashboard.html",
            context={"seasons": seasons, "view": view_type},
        )

    @get(
        [urls.ADMIN_SEASON_CREATE],
        status_code=HTTPStatus.OK,
        name="get_season_create",
        cache_control=CacheControlHeader(must_revalidate=False),
    )
    async def get_season_create(self, request: HTMXRequest) -> Template | Redirect:
        if request.htmx:
            request.logger.info("htmx")
            return htmx_template(
                template_name="admin/partials/season-create.html",
                block_name="admin_panel",
            )
        return htmx_template(template_name="admin/partials/season-create.html")

    @post(
        [urls.ADMIN_SEASON_CREATE],
        status_code=HTTPStatus.CREATED,
        name="post_season_create",
        dto=SeasonCreateDTO,
        return_dto=None,
        dependencies={"season_service": provide_season_service},
    )
    async def post_season_create(
        self,
        request: HTMXRequest,
        season_service: SeasonService,
        data: Annotated[Season, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect | None:
        request.logger.info(f"admin season create: {data.to_dict()}")
        try:
            await season_service.create(
                data=data, auto_commit=True
            )  # write to database
        except ConflictError:
            return Redirect(path=urls.ADMIN_SEASON)
        finally:
            # ignore the validation error but dont issue post
            pass
        return Redirect(path=urls.ADMIN_SEASON)

    @get(
        [urls.ADMIN_SEASON_EDIT],
        status_code=HTTPStatus.OK,
        name="get_season_edit",
        dependencies={
            "season_repo": provide_season_repo,
            "league_repo": provide_league_repo,
        },
        dto=SeasonUpdateDTO,
    )
    async def get_season_edit(
        self,
        request: HTMXRequest,
        season_repo: SeasonRepo,
        league_repo: LeagueRepo,
        slug: str,
    ) -> Template:
        season_data = await season_repo.get_by_slug(slug)
        if season_data:
            leagues, _ = await season_repo.get_season_leagues(season_id=season_data.id)
        if season_data:
            season = season_data.to_dict()
        request.logger.info(f"leagues {leagues}")
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/season-edit.html",
                context={
                    "season": season,
                    "leagues": leagues,
                },
            )
        return htmx_template(template_name="admin/dashboard.html")

    @post(
        [urls.ADMIN_SEASON_EDIT],
        status_code=HTTPStatus.CREATED,
        name="post_season_edit",
        dependencies={"season_service": provide_season_service},
        return_dto=None,
        dto=SeasonUpdateDTO,
    )
    async def post_season_edit(
        self,
        request: HTMXRequest,
        season_service: SeasonService,
        data: Annotated[Season, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        await season_service.update(
            data=data, item_id=data.id, auto_commit=True
        )  # write to database
        return Redirect(path=urls.ADMIN_SEASON)


    @get(
        [urls.ADMIN_SEASON_END_DATE],
        status_code=HTTPStatus.OK,
        name="get_season_end_date",
    )
    async def get_season_end_date(self, request: HTMXRequest) -> Template:
        return htmx_template(template_name="admin/partials/season-edit.html", context={"show_end_date": True}, block_name="end_season")

    @post(
        [urls.ADMIN_SEASON_SEARCH],
        status_code=HTTPStatus.OK,
        name="post_season_search",
        dependencies={"season_repo": provide_season_repo},
    )
    async def post_season_search(
        self,
        request: HTMXRequest,
        season_repo: SeasonRepo,
        data: Annotated[dict, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Template:
        request.logger.info(f"admin season search: {data}")
        try:
            season = await season_repo.get_one(name=data["name"])
        except NotFoundError:
            season = None
        request.logger.info(f"{season=}")
        if season:
            return htmx_template(
                template_name="admin/partials/season-create.html",
                context={"duplicate": True, "season": season.to_dict()},
                block_name="confirmation_buttons",
            )
        return htmx_template(
            template_name="admin/partials/season-create.html",
            block_name="confirmation_buttons",
        )

    @get(
        [urls.ADMIN_SEASON_DELETE],
        status_code=HTTPStatus.OK,
        dependencies={"season_repo": provide_season_repo},
        name="get_season_delete",
    )
    async def get_season_delete(
        self,
        request: HTMXRequest,
        season_repo: SeasonRepo,
        slug: str,
    ) -> Template:
        data = await season_repo.get_by_slug(slug)
        if data:
            season = data.to_dict()
        request.logger.info(f"{request.headers}")
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/season-edit.html",
                context={"confirm": True, "season": season},
                block_name="delete_confirm",
            )

        return htmx_template(template_name="admin/dashboard.html")

    @delete(
        [urls.ADMIN_SEASON_DELETE],
        status_code=HTTPStatus.CREATED,
        name="delete_season",
        dependencies={"season_repo": provide_season_repo},
    )
    async def delete_season(
        self,
        request: HTMXRequest,
        season_repo: SeasonRepo,
    ) -> Template:
        request.logger.info(f"id: {request.headers.get("season_id")}")
        if request.headers.get("season_id"):
            _ = await season_repo.delete(item_id=request.headers.get("season_id"))
        seasons = await season_repo.list()
        print(seasons)
        return htmx_template(
            template_name="admin/partials/season-index.html",
            context={"seasons": seasons, "view": "tile_view"},
        )
