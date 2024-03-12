from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from advanced_alchemy.exceptions import ConflictError, NotFoundError
from litestar import Controller, delete, get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.datastructures import CacheControlHeader
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect, Template

from app.controllers import urls
from app.core.response import htmx_template
from app.dto import TeamCreateDTO, TeamUpdateDTO
from app.models import Team
from app.services import (
    provide_league_repo,
    provide_team_repo,
    provide_team_service,
)
from app.services.iesl import LeagueRepo, TeamRepo, TeamService


class AdminTeamController(Controller):
    guards = []
    cache_control = CacheControlHeader(
        no_cache=True, no_store=True, must_revalidate=True
    )

    @get(
        [urls.ADMIN_TEAM],
        status_code=HTTPStatus.OK,
        name="admin_team",
        dependencies={"team_service": provide_team_service},
    )
    async def get_teams(
        self, team_service: TeamService, request: HTMXRequest
    ) -> Template:
        teams = await team_service.list()

        if request.htmx:
            return htmx_template(
                template_name="admin/partials/team-index.html",
                context={"teams": teams},
            )
        return htmx_template(
            template_name="admin/dashboard.html", context={"teams": teams}
        )

    @get(
        [urls.ADMIN_TEAM_CREATE],
        status_code=HTTPStatus.OK,
        name="get_team_create",
        dependencies={"league_repo": provide_league_repo},
    )
    async def get_team_create(
        self, league_repo: LeagueRepo, request: HTMXRequest
    ) -> Template:
        leagues = await league_repo.list()
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/team-create.html",
                context={"leagues": leagues},
                block_name="admin_panel",
            )
        return htmx_template(
            template_name="admin/partials/team-create.html",
            context={"leagues": leagues},
        )

    @post(
        [urls.ADMIN_TEAM_CREATE],
        status_code=HTTPStatus.CREATED,
        name="post_team_create",
        dto=TeamCreateDTO,
        return_dto=None,
        dependencies={"team_service": provide_team_service},
    )
    async def post_team_create(
        self,
        request: HTMXRequest,
        team_service: TeamService,
        data: Annotated[Team, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect | None:
        request.logger.info(f"admin team create: {data.to_dict()}")
        try:
            await team_service.create(data=data, auto_commit=True)  # write to database
        except ConflictError:
            return Redirect(path=urls.ADMIN_TEAM)
        finally:
            # ignore the validation error but dont issue post
            pass
        return Redirect(path=urls.ADMIN_TEAM)

    @get(
        [urls.ADMIN_TEAM_EDIT],
        status_code=HTTPStatus.OK,
        name="get_team_edit",
        dependencies={
            "team_repo": provide_team_repo,
            "league_repo": provide_league_repo,
        },
        dto=TeamUpdateDTO,
    )
    async def get_team_edit(
        self,
        request: HTMXRequest,
        team_repo: TeamRepo,
        league_repo: LeagueRepo,
        slug: str,
    ) -> Template:
        team_data = await team_repo.get_by_slug(slug)
        leagues = await league_repo.list()
        if team_data := await team_repo.get_by_slug(slug):
            request.logger.info(f"admin team edit: {team_data.to_dict()}")

        if request.htmx:
            return htmx_template(
                template_name="admin/partials/team-edit.html",
                context={
                    "team": team_data,
                    "show_end_date": True,
                    "leagues": leagues,
                },
            )
        return htmx_template(template_name="admin/dashboard.html")

    @post(
        [urls.ADMIN_TEAM_EDIT],
        status_code=HTTPStatus.CREATED,
        name="post_team_edit",
        dependencies={
            "team_service": provide_team_service,
            # "season_repo": provide_season_repo,
        },
        dto=TeamUpdateDTO,
        return_dto=None,
    )
    async def post_team_edit(
        self,
        request: HTMXRequest,
        team_service: TeamService,
        data: Annotated[Team, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        request.logger.info(f"From post team edit: {data.to_dict()}")
        try:
            await team_service.update(
                data=data.to_dict(), item_id=data.id, auto_commit=True
            )  # write to database
        except ConflictError as e:
            request.logger.exception("error", exc_info=e)
            return Redirect(path=urls.ADMIN_TEAM)
        finally:
            # ignore the validation error but dont issue post
            pass
        return Redirect(path=urls.ADMIN_TEAM)

    @post(
        [urls.ADMIN_TEAM_SEARCH],
        status_code=HTTPStatus.OK,
        name="post_team_search",
        dependencies={"team_repo": provide_team_repo},
    )
    async def post_team_search(
        self,
        request: HTMXRequest,
        team_repo: TeamRepo,
        data: Annotated[dict, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Template:
        try:
            team = await team_repo.get_one(name=data["name"])
        except NotFoundError:
            team = None
        request.logger.info(f"{team=}")
        if team:
            return htmx_template(
                template_name="admin/partials/team-create.html",
                context={"duplicate": True, "team": team.to_dict()},
                block_name="confirmation_buttons",
            )
        return htmx_template(
            template_name="admin/partials/team-create.html",
            block_name="confirmation_buttons",
        )

    @get(
        [urls.ADMIN_TEAM_DELETE],
        status_code=HTTPStatus.OK,
        dependencies={"team_repo": provide_team_repo},
        name="get_team_delete",
    )
    async def get_team_delete(
        self,
        request: HTMXRequest,
        team_repo: TeamRepo,
        slug: str,
    ) -> Template:
        data = await team_repo.get_by_slug(slug)
        if data:
            team = data.to_dict()
        request.logger.info(f"{request.headers}")
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/team-edit.html",
                context={"confirm": True, "team": team},
                block_name="delete_confirm",
            )

        return htmx_template(template_name="admin/dashboard.html")

    @delete(
        [urls.ADMIN_TEAM_DELETE],
        status_code=HTTPStatus.CREATED,
        name="delete_team",
        dependencies={"team_repo": provide_team_repo},
    )
    async def delete_team(
        self,
        request: HTMXRequest,
        team_repo: TeamRepo,
    ) -> Template:
        request.logger.info(f"id: {request.headers.get("team_id")}")
        if request.headers.get("team_id"):
            _ = await team_repo.delete(item_id=request.headers.get("team_id"))
        teams = await team_repo.list()
        print(teams)
        return htmx_template(
            template_name="admin/partials/team-index.html",
            context={"teams": teams, "view": "tile_view"},
        )
