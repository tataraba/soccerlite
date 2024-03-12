from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Fixture, FixtureTeam, League, Schedule, Season, Team

from .iesl import (
    FixtureRepo,
    FixtureService,
    FixtureTeamRepo,
    FixtureTeamService,
    LeagueRepo,
    LeagueService,
    ScheduleRepo,
    ScheduleService,
    SeasonRepo,
    SeasonService,
    TeamRepo,
    TeamService,
)


async def provide_season_repo(db_session: AsyncSession) -> SeasonRepo:
    return SeasonRepo(session=db_session, statement=select(Season))


async def provide_league_repo(db_session: AsyncSession) -> LeagueRepo:
    return LeagueRepo(session=db_session, statement=select(League))


async def provide_team_repo(db_session: AsyncSession) -> TeamRepo:
    return TeamRepo(session=db_session, statement=select(Team))


async def provide_fixture_repo(db_session: AsyncSession) -> FixtureRepo:
    return FixtureRepo(session=db_session, statement=select(Fixture))


async def provide_fixture_teams_repo(db_session: AsyncSession) -> FixtureTeamRepo:
    return FixtureTeamRepo(session=db_session, statement=select(FixtureTeam))


async def provide_schedule_repo(db_session: AsyncSession) -> ScheduleRepo:
    return ScheduleRepo(session=db_session, statement=select(Schedule))


async def provide_season_service(
    db_session: AsyncSession | None = None
) -> AsyncGenerator[SeasonService, None]:
    async with SeasonService.new(
        session=db_session, statement=select(Season)
    ) as service:
        yield service


async def provide_league_service(
    db_session: AsyncSession | None = None
) -> AsyncGenerator[LeagueService, None]:
    async with LeagueService.new(
        session=db_session,
    ) as service:
        yield service


async def provide_team_service(
    db_session: AsyncSession | None = None
) -> AsyncGenerator[TeamService, None]:
    async with TeamService.new(
        session=db_session,
    ) as service:
        yield service


async def provide_fixture_service(
    db_session: AsyncSession | None = None
) -> AsyncGenerator[FixtureService, None]:
    async with FixtureService.new(
        session=db_session,
    ) as service:
        yield service


async def provide_fixture_team_service(
    db_session: AsyncSession | None = None
) -> AsyncGenerator[FixtureTeamService, None]:
    async with FixtureTeamService.new(
        session=db_session,
    ) as service:
        yield service


async def provide_schedule_service(
    db_session: AsyncSession | None = None
) -> AsyncGenerator[ScheduleService, None]:
    async with ScheduleService.new(
        session=db_session,
    ) as service:
        yield service
