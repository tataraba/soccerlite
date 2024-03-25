from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated, Any
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
from app.core.toolbox import convert_utc_to_pst
from app.dto import (
    FixtureCreateDTO,
    FixtureDTO,
    ScheduleCreateDTO,
    ScheduleDTO,
    ScheduleUpdateDTO,
)
from app.models import Field, FixtureStatus, Schedule, Team
from app.services import (
    provide_fixture_repo,
    provide_fixture_service,
    provide_fixture_team_service,
    provide_fixture_teams_repo,
    provide_league_repo,
    provide_schedule_repo,
    provide_schedule_service,
    provide_team_repo,
    provide_team_service,
)
from app.services.iesl import (
    FixtureRepo,
    FixtureService,
    FixtureTeamService,
    LeagueRepo,
    ScheduleRepo,
    ScheduleService,
    TeamRepo,
    TeamService,
)


class AdminScheduleController(Controller):
    guards = []
    cache_control = CacheControlHeader(
        no_cache=True, no_store=True, must_revalidate=True
    )

    @get(
        [urls.ADMIN_SCHEDULE],
        status_code=HTTPStatus.OK,
        name="admin_schedule",
        dependencies={"schedule_service": provide_schedule_service},
    )
    async def get_schedules(
        self, schedule_service: ScheduleService, request: HTMXRequest
    ) -> Template:
        schedules = []
        _schedules = await schedule_service.list()
        for s in _schedules:
            _schedule = await schedule_service.get_league_name(s.league_id)
            schedules.append(_schedule)
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/schedule-index.html",
                context={"schedules": schedules},
            )
        return htmx_template(
            template_name="admin/dashboard.html", context={"schedules": schedules}
        )

    @get(
        [urls.ADMIN_SCHEDULE_CREATE],
        status_code=HTTPStatus.OK,
        name="get_schedule_create",
        dependencies={"league_repo": provide_league_repo},
    )
    async def get_schedule_create(
        self, league_repo: LeagueRepo, request: HTMXRequest
    ) -> Template:
        leagues_without_schedule = await league_repo.list_without_schedule()
        block_name = None
        if request.htmx:
            block_name = "admin_panel"
        return htmx_template(
            template_name="admin/partials/schedule-create.html",
            context={"leagues": leagues_without_schedule},
            block_name=block_name,
        )

    @get(
        [urls.ADMIN_SCHEDULE_LEAGUE],
        status_code=HTTPStatus.OK,
        name="get_schedule_league",
        dependencies={
            "league_repo": provide_league_repo,
            "schedule_repo": provide_schedule_repo,
        },
    )
    async def get_schedule_league(
        self,
        league_repo: LeagueRepo,
        schedule_repo: ScheduleRepo,
        request: HTMXRequest,
        league_id: UUID,
    ) -> Template:
        # leagues = await league_repo.list()
        league = await league_repo.get(league_id)
        context: dict[str, Any] = {"league": league}
        try:
            schedule = await schedule_repo.get_schedule_for_league(league_id)
            context["schedule"] = schedule
        except ValueError:
            pass
        block_name = "confirmation_buttons"
        if request.htmx:
            request.logger.info(f"{context=}")
            return htmx_template(
                template_name="admin/partials/schedule-create.html",
                context=context,
                block_name=block_name,
            )
        return htmx_template(
            template_name="admin/dashboard.html",
            context=context,
            block_name=block_name,
        )

    @post(
        [urls.ADMIN_SCHEDULE_CREATE],
        status_code=HTTPStatus.CREATED,
        name="post_schedule_create",
        dto=ScheduleCreateDTO,
        return_dto=None,
        dependencies={
            "schedule_service": provide_schedule_service,
            "fixture_team_service": provide_fixture_team_service,
            "team_service": provide_team_service,
        },
    )
    async def post_schedule_create(
        self,
        request: HTMXRequest,
        schedule_service: ScheduleService,
        fixture_team_service: FixtureTeamService,
        team_service: TeamService,
        data: Annotated[Schedule, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect | None:
        try:
            teams = await team_service.list_from_league(league_id=data.league_id)
            if not teams:
                return Redirect(path=urls.ADMIN_SCHEDULE)
            schedule = await schedule_service.create(
                data=data, auto_commit=True
            )  # write to database

            _ = await fixture_team_service.generate_fixtures(
                schedule=schedule,
                teams=teams,
                start_date=data.scheduled_start,
            )

        except ConflictError:
            return Redirect(path=urls.ADMIN_SCHEDULE)
        finally:
            # ignore the validation error but dont issue post
            pass

        return Redirect(path=urls.ADMIN_SCHEDULE)

    @post(
        urls.ADMIN_SCHEDULE_GENERATE,
        status_code=HTTPStatus.CREATED,
        name="post_schedule_generate",
        dependencies={
            "schedule_service": provide_schedule_service,
            "fixture_service": provide_fixture_service,
            "team_repo": provide_team_repo,
        },
    )
    async def post_generate_fixtures(
        self,
        request: HTMXRequest,
        schedule_service: ScheduleService,
        fixture_service: FixtureService,
        team_repo: TeamRepo,
    ) -> Redirect | None:
        # await fixture_service.generate_fixtures()
        return Redirect(path=urls.ADMIN_SCHEDULE)

    @get(
        [urls.ADMIN_SCHEDULE_VIEW],
        status_code=HTTPStatus.OK,
        name="get_schedule_view",
        dependencies={
            "schedule_repo": provide_schedule_repo,
            "fixture_repo": provide_fixture_repo,
            "team_repo": provide_team_repo,
        },
        dto=ScheduleUpdateDTO,
    )
    async def get_schedule_view(
        self,
        request: HTMXRequest,
        schedule_repo: ScheduleRepo,
        fixture_repo: FixtureRepo,
        team_repo: TeamRepo,
        slug: str,
    ) -> Template:
        schedule = await schedule_repo.get_by_slug(slug)
        if schedule:
            fixtures = await fixture_repo.list_from_schedule(schedule_id=schedule.id)
            teams = await team_repo.list(league_id=schedule.league_id)

        context = {
            "schedule": schedule,
            "fixtures": fixtures,
            "teams": teams,
            "utc_to_pst": convert_utc_to_pst,
        }
        block_name = None
        if request.htmx:
            block_name = "admin_panel"
        return htmx_template(
            template_name="admin/partials/schedule-view.html",
            context=context,
            block_name=block_name,
        )

    @get(
        [urls.ADMIN_SCHEDULE_EDIT],
        status_code=HTTPStatus.OK,
        name="get_schedule_edit",
        dependencies={
            "schedule_repo": provide_schedule_repo,
            "fixture_repo": provide_fixture_repo,
            "team_repo": provide_team_repo,
        },
        dto=ScheduleUpdateDTO,
    )
    async def get_schedule_edit(
        self,
        request: HTMXRequest,
        schedule_repo: ScheduleRepo,
        fixture_repo: FixtureRepo,
        team_repo: TeamRepo,
        slug: str,
    ) -> Template:
        fixtures = []
        teams = []
        schedule = await schedule_repo.get_by_slug(slug)
        if schedule:
            fixtures = await fixture_repo.list_from_schedule(schedule_id=schedule.id)
            teams = await team_repo.list(league_id=schedule.league_id)
        context = {
            "schedule": schedule,
            "fixtures": fixtures,
            "teams": teams,
            "game_status": FixtureStatus,
            "utc_to_pst": convert_utc_to_pst,
            "field": Field,
        }
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/schedule-edit.html",
                context=context,
                block_name="admin_panel",
            )
        return htmx_template(
            template_name="admin/partials/schedule-edit.html",
            context=context,
        )

    @get(
        [urls.ADMIN_SCHEDULE_DELETE],
        status_code=HTTPStatus.OK,
        dependencies={"schedule_repo": provide_schedule_repo},
        name="get_schedule_delete",
    )
    async def get_schedule_delete(
        self,
        request: HTMXRequest,
        schedule_repo: ScheduleRepo,
        slug: str,
    ) -> Template:
        if _data := await schedule_repo.get_by_slug(slug):
            schedule = _data.to_dict()
        if request.htmx:
            return htmx_template(
                template_name="admin/partials/schedule-edit.html",
                context={"confirm": True, "schedule": schedule},
                block_name="delete_confirm",
            )

        return htmx_template(template_name="admin/dashboard.html")

    @delete(
        [urls.ADMIN_SCHEDULE_DELETE],
        status_code=HTTPStatus.CREATED,
        name="delete_schedule",
        dependencies={"schedule_repo": provide_schedule_repo},
    )
    async def delete_schedule(
        self,
        request: HTMXRequest,
        schedule_repo: ScheduleRepo,
    ) -> Template:
        if request.headers.get("schedule_id"):
            _ = await schedule_repo.delete(item_id=request.headers.get("schedule_id"))
        schedules = await schedule_repo.list()

        return htmx_template(
            template_name="admin/partials/schedule-index.html",
            context={"schedules": schedules, "view": "tile_view"},
        )
