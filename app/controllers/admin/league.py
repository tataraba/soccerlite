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
from app.dto import LeagueCreateDTO, LeagueUpdateDTO
from app.models import Category, Division, League, MatchDay
from app.services import (
    provide_league_repo,
    provide_league_service,
    provide_season_repo,
)
from app.services.iesl import LeagueRepo, LeagueService, SeasonRepo


class AdminLeagueController(Controller):
    guards = []
    cache_control = CacheControlHeader(
        no_cache=True, no_store=True, must_revalidate=True
    )

    @get(
        [urls.ADMIN_LEAGUE],
        status_code=HTTPStatus.OK,
        name="admin_league",
        dependencies={"league_service": provide_league_service},
    )
    async def get_leagues(
        self, league_service: LeagueService, request: HTMXRequest
    ) -> Template:
        leagues = await league_service.list()

        if request.htmx:
            return htmx_template(
                template_name="admin/partials/league-index.html",
                context={"leagues": leagues},
            )
        return htmx_template(
            template_name="admin/dashboard.html", context={"leagues": leagues}
        )

    @get(
        [urls.ADMIN_LEAGUE_CREATE],
        status_code=HTTPStatus.OK,
        name="get_league_create",
        dependencies={"season_repo": provide_season_repo},
    )
    async def get_league_create(
        self, request: HTMXRequest, season_repo: SeasonRepo
    ) -> Template:
        seasons = await season_repo.list()
        block_name = None

        if request.htmx:
            block_name = "admin_panel"

        return htmx_template(
            template_name="admin/partials/league-create.html",
            context={"seasons": seasons},
            block_name=block_name,
        )

    @post(
        [urls.ADMIN_LEAGUE_CREATE],
        status_code=HTTPStatus.OK,
        name="post_league_create",
        dto=LeagueCreateDTO,
        return_dto=None,
        dependencies={"league_service": provide_league_service},
    )
    async def post_league_create(
        self,
        request: HTMXRequest,
        league_service: LeagueService,
        data: Annotated[League, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        try:
            await league_service.create(
                data=data, auto_commit=True
            )  # write to database
        except ConflictError as e:
            request.logger.exception("error", exc_info=e)
            return Redirect(path=urls.ADMIN_LEAGUE)
        finally:
            # ignore the validation error but dont issue post
            pass
        return Redirect(path=urls.ADMIN_LEAGUE)

    @get(
        [urls.ADMIN_LEAGUE_EDIT],
        status_code=HTTPStatus.OK,
        name="get_league_edit",
        dependencies={
            "league_repo": provide_league_repo,
            "season_repo": provide_season_repo,
        },
        dto=LeagueUpdateDTO,
    )
    async def get_league_edit(
        self,
        request: HTMXRequest,
        league_repo: LeagueRepo,
        season_repo: SeasonRepo,
        slug: str,
    ) -> Template:
        league_data = await league_repo.get_by_slug(slug)
        if league_data:
            print(league_data.to_dict())
        seasons = await season_repo.list()

        if request.htmx:
            return htmx_template(
                template_name="admin/partials/league-edit.html",
                context={
                    "league": league_data,
                    "show_end_date": True,
                    "seasons": seasons,
                    "divisions": Division,
                    "categories": Category,
                    "match_days": MatchDay,
                    "ages": [0, 20, 30, 40, 50],
                },
            )
        return htmx_template(template_name="admin/dashboard.html")

    @post(
        [urls.ADMIN_LEAGUE_EDIT],
        status_code=HTTPStatus.CREATED,
        name="post_league_edit",
        dependencies={
            "league_service": provide_league_service,
            # "season_repo": provide_season_repo,
        },
        dto=LeagueUpdateDTO,
        return_dto=None,
    )
    async def post_league_edit(
        self,
        request: HTMXRequest,
        league_service: LeagueService,
        data: Annotated[League, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        try:
            await league_service.update(
                data=data.to_dict(), item_id=data.id, auto_commit=True
            )  # write to database
        except ConflictError as e:
            request.logger.exception("error", exc_info=e)
            return Redirect(path=urls.ADMIN_LEAGUE)
        finally:
            # ignore the validation error but dont issue post
            pass
        return Redirect(path=urls.ADMIN_LEAGUE)

    @get(
        [urls.ADMIN_LEAGUE_AGE_OVER],
        status_code=HTTPStatus.OK,
        name="get_league_age_over",
    )
    async def get_league_age_over(self, category: str) -> Template:
        print(category)
        return htmx_template(
            template_name="admin/partials/league-create.html",
            context={"category": category},
            block_name="age_over",
        )

    @post(
        [urls.ADMIN_LEAGUE_SEARCH],
        status_code=HTTPStatus.OK,
        name="post_league_search",
        dependencies={"league_repo": provide_league_repo},
    )
    async def post_league_search(
        self,
        request: HTMXRequest,
        league_repo: LeagueRepo,
        data: Annotated[dict, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Template:
        try:
            league = await league_repo.get_one(name=data["name"])
        except NotFoundError:
            league = None
        if league:
            return htmx_template(
                template_name="admin/partials/league-create.html",
                context={"duplicate": True, "league": league.to_dict()},
                block_name="confirmation_buttons",
            )
        return htmx_template(
            template_name="admin/partials/league-create.html",
            block_name="confirmation_buttons",
        )

    @get(
        [urls.ADMIN_LEAGUE_DELETE],
        status_code=HTTPStatus.OK,
        dependencies={"league_repo": provide_league_repo},
        name="get_league_delete",
    )
    async def get_league_delete(
        self,
        request: HTMXRequest,
        league_repo: LeagueRepo,
        slug: str,
    ) -> Template:
        if _data := await league_repo.get_by_slug(slug):
            league = _data.to_dict()
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/league-edit.html",
                context={"confirm": True, "league": league},
                block_name="delete_confirm",
            )

        return htmx_template(template_name="admin/dashboard.html")

    @delete(
        [urls.ADMIN_LEAGUE_DELETE],
        status_code=HTTPStatus.CREATED,
        name="delete_league",
        dependencies={"league_repo": provide_league_repo},
    )
    async def delete_league(
        self,
        request: HTMXRequest,
        league_repo: LeagueRepo,
    ) -> Template:
        if request.headers.get("league_id"):
            _ = await league_repo.delete(item_id=request.headers.get("league_id"))
        leagues = await league_repo.list()

        return htmx_template(
            template_name="admin/partials/league-index.html",
            context={"leagues": leagues, "view": "tile_view"},
        )
