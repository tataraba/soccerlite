from __future__ import annotations

from datetime import timedelta
from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated, Any
from uuid import UUID

from advanced_alchemy.exceptions import ConflictError, NotFoundError
from advanced_alchemy.filters import CollectionFilter, OrderBy, SearchFilter
from litestar import Controller, delete, get, post
from litestar.contrib.htmx.request import HTMXRequest
from litestar.datastructures import CacheControlHeader
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.response import Redirect, Template

from app.controllers import urls
from app.core.response import htmx_template
from app.dto import (
    FixtureCreateDTO,
    FixtureDTO,
    FixtureScheduleDTO,
    FixtureUpdateDTO,
    ScheduleCreateDTO,
    ScheduleDTO,
    ScheduleUpdateDTO,
)
from app.models import Field, Fixture, FixtureStatus, Schedule, Team
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


class AdminFixtureController(Controller):
    guards = []
    cache_control = CacheControlHeader(
        no_cache=True, no_store=True, must_revalidate=True
    )

    @get(
        [urls.ADMIN_FIXTURE_EDIT],
        status_code=HTTPStatus.OK,
        name="get_fixture_edit",
        dependencies={
            "schedule_repo": provide_schedule_repo,
            "fixture_service": provide_fixture_service,
            "team_repo": provide_team_repo,
        },
        dto=FixtureScheduleDTO,
    )
    async def get_fixture_edit(
        self,
        schedule_repo: ScheduleRepo,
        fixture_service: FixtureService,
        team_repo: TeamRepo,
        request: HTMXRequest,
        id: UUID,
    ) -> Template:
        # fixtures = []
        fixture = await fixture_service.get(id)
        schedule = await schedule_repo.get(fixture.schedule_id)
        teams = await team_repo.list_from_league(league_id=schedule.league_id)
        # fixtures.append(fixture)
        context = {
            "fixtures": [fixture],
            "teams": teams,
            "game_status": FixtureStatus,
            "field": Field,
            "cancelled": True,
        }
        return htmx_template(
            template_name="admin/partials/schedule-edit.html",
            context=context,
            block_name="fixture_edit",
        )

    @post(
        [urls.ADMIN_FIXTURE_EDIT],
        status_code=HTTPStatus.CREATED,
        name="post_fixture_edit",
        dependencies={
            "schedule_repo": provide_schedule_repo,
            "fixture_service": provide_fixture_service,
            "team_repo": provide_team_repo,
        },
        dto=FixtureUpdateDTO,
    )
    async def edit_fixture(
        self,
        schedule_repo: ScheduleRepo,
        fixture_service: FixtureService,
        team_repo: TeamRepo,
        request: HTMXRequest,
        data: Annotated[Fixture, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Template | Redirect:
        fixtures = []
        try:
            fixture = await fixture_service.update(
                data=data.to_dict(), item_id=data.id, auto_commit=True
            )  # write to database
        except ConflictError as e:
            request.logger.exception("error", exc_info=e)
            return Redirect(path=urls.ADMIN_SCHEDULE_EDIT)
        finally:
            # ignore the validation error but dont issue post
            pass
        schedule = await schedule_repo.get(fixture.schedule_id)
        teams = await team_repo.list_from_league(league_id=schedule.league_id)
        fixtures.append(fixture)
        context = {
            "fixtures": fixtures,
            "teams": teams,
            "game_status": FixtureStatus,
            "field": Field,
            "updated": True,
        }
        return htmx_template(
            template_name="admin/partials/schedule-edit.html",
            context=context,
            block_name="fixture_edit",
        )

    @post(
        [urls.ADMIN_SCHEDULE_PUSH],
        status_code=HTTPStatus.CREATED,
        name="post_schedule_push",
        dependencies={
            "schedule_service": provide_schedule_service,
            "fixture_service": provide_fixture_service,
            "team_service": provide_team_service,
        },
        dto=FixtureUpdateDTO,
    )
    async def post_schedule_push(
        self,
        request: HTMXRequest,
        schedule_service: ScheduleService,
        fixture_service: FixtureService,
        team_service: TeamService,
        data: Annotated[Fixture, Body(media_type=RequestEncodingType.URL_ENCODED)],
    ) -> Redirect:
        fixtures = []
        fixture = await fixture_service.get(item_id=data.id)
        schedule = await schedule_service.get(item_id=fixture.schedule_id)
        if not fixture.schedule_id:
            raise ConflictError("Fixture is not associated with a schedule")

        matchday_fixtures = await fixture_service.list_of_matchday_fixtures(
            SearchFilter("team_away_name", "FR Pate"),
            schedule_id=fixture.schedule_id,
            matchday=fixture.matchday,
        )
        if last_day_on_schedule := await fixture_service.last_date_on_schedule(
            fixture.schedule_id,
        ):
            for matchday_fixture in matchday_fixtures:
                matchday_fixture.game_date = last_day_on_schedule + timedelta(days=7)
                fixtures.append(matchday_fixture)

        await fixture_service.update_many(fixtures, auto_commit=True)

        return Redirect(path=f"/iesl-admin/schedule/edit/{schedule.slug}")
