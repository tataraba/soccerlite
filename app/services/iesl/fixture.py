import logging
from collections import deque
from datetime import UTC, datetime, timedelta
from itertools import chain
from random import shuffle
from typing import Any
from uuid import UUID

from advanced_alchemy import FilterTypes
from advanced_alchemy.filters import BeforeAfter, OrderBy
from sqlalchemy import select

from app import models
from app.services.base import (
    SQLAlchemyAsyncRepositoryService,
    SQLAlchemyAsyncSlugRepository,
)

__all__ = [
    "FixtureRepo",
    "FixtureTeamRepo",
    "FixtureService",
    "FixtureTeamService",
]


class FixtureRepo(SQLAlchemyAsyncSlugRepository[models.Fixture]):
    model_type = models.Fixture

    async def upcoming_fixtures(self, *filters: FilterTypes, **kwargs: Any):
        statement = (
            (
                select(models.Fixture, models.League)
                .join_from(models.Fixture, models.Schedule)
                .join_from(models.Schedule, models.League)
            )
            .filter(
                models.Fixture.game_date.between(
                    datetime.now(UTC), datetime.now(UTC) + timedelta(days=6)
                )
            )
            .order_by(
                models.League.name,
                models.Fixture.game_date,
                models.Fixture.field,
            )
        )

        fixtures = await self.session.execute(
            statement=statement,
        )
        return fixtures.all()

    async def list_from_schedule(
        self,
        *filters: FilterTypes,
        schedule_id: UUID,
        **kwargs: Any,
    ) -> list[models.Fixture]:
        return await self.list(
            OrderBy(field_name="game_date", sort_order="asc"),
            OrderBy(field_name="field", sort_order="asc"),
            statement=select(models.Fixture).where(
                models.Fixture.schedule_id == schedule_id
            ),
        )

    async def list_of_matchday_fixtures(
        self,
        *filters: FilterTypes,
        schedule_id: UUID,
        matchday: int,
        **kwargs: Any,
    ) -> list[models.Fixture]:
        return await self.list(
            OrderBy(field_name="game_date", sort_order="asc"),
            OrderBy(field_name="field", sort_order="asc"),
            statement=select(models.Fixture).where(
                models.Fixture.schedule_id == schedule_id,
                models.Fixture.matchday == matchday,
            ),
        )

    async def last_date_on_schedule(self, schedule_id: UUID) -> datetime:
        statement = (
            select(models.Fixture)
            .where(models.Fixture.schedule_id == schedule_id)
            .order_by(models.Fixture.game_date.desc())
        )
        result = await self.session.execute(statement=statement)
        fixture = result.scalar()
        if not fixture:
            raise ValueError(f"Couldn't find fixture for {self.model_type}.")
        return fixture.game_date


class FixtureTeamRepo(SQLAlchemyAsyncSlugRepository[models.FixtureTeam]):
    model_type = models.FixtureTeam


class FixtureService(SQLAlchemyAsyncRepositoryService[models.Fixture]):
    repository_type = FixtureRepo

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: FixtureRepo = self.repository_type(**repo_kwargs)

    async def list_from_schedule(
        self,
        *filters: FilterTypes,
        schedule_id: UUID,
        **kwargs: Any,
    ) -> list[models.Fixture]:
        return await self.repository.list_from_schedule(
            *filters, schedule_id=schedule_id, **kwargs
        )

    async def list_of_matchday_fixtures(
        self,
        *filters: FilterTypes,
        schedule_id: UUID,
        matchday: int,
        **kwargs: Any,
    ) -> list[models.Fixture]:
        return await self.repository.list_of_matchday_fixtures(
            *filters, schedule_id=schedule_id, matchday=matchday, **kwargs
        )

    async def last_date_on_schedule(self, schedule_id: UUID) -> datetime:
        return await self.repository.last_date_on_schedule(schedule_id)


class FixtureTeamService(SQLAlchemyAsyncRepositoryService[models.FixtureTeam]):
    repository_type = FixtureTeamRepo

    def __init__(self, **repo_kwargs: Any) -> None:
        self.repository: FixtureTeamRepo = self.repository_type(**repo_kwargs)

    async def generate_fixtures(
        self,
        schedule: models.Schedule,
        teams: list[models.Team],
        shuffle_teams: bool = False,
        **kwargs: Any,
    ):
        fixtures = []
        round_number = 1
        if shuffle_teams:
            # Randomizes matchups to vary between seasons
            shuffle(teams)
        teams = add_bye_week_team(schedule, teams)
        matches_per_round = len(teams) - 1

        rounds, remaining = divmod(schedule.total_games, matches_per_round)

        for matchday in range(schedule.total_games):
            round_number = matchday // matches_per_round
            logging.info(f"round_number: {round_number}")
            if round_number < rounds:
                round_number = round_number + 1
                _fixtures = create_fixtures(schedule, teams, matchday, round_number)
                fixtures.extend(_fixtures)
            elif remaining and round_number == rounds:
                logging.info(f"This is for remaining games {remaining=}")
                # CREATE FIXTURES FOR PLAYOFF GAMES
                break
            else:
                logging.info("outside of defined set")
                pass

        _ = await self.create_many(fixtures, auto_commit=True, auto_expunge=True)
        return fixtures


def create_fixtures(
    schedule: models.Schedule,
    teams: list[models.Team],
    matchday: int,
    round_number: int,
):
    fixtures = []
    rotate = True
    if matchday == 0:
        rotate = False

    matchups = create_matchups(teams=teams, matchday=matchday, rotate=rotate)

    for count, match in enumerate(matchups, start=1):
        field = determine_field(schedule=schedule, count=count)
        team_home, team_away = home_or_away(round_number=round_number, match=match)
        game_date = weekly_increment(schedule=schedule, num_weeks=matchday)
        game_date_time = determine_time(
            schedule=schedule,
            start_time=game_date,
            count=count,
            match_count=len(matchups),
        )

        fixture = models.Fixture(
            schedule_id=schedule.id,
            team_home_id=team_home.id,
            team_away_id=team_away.id,
            matchday=matchday + 1,
            game_date=game_date_time,
            field=field,
            game_status=models.FixtureStatus.UNPLAYED,
        )

        fixtures.append(fixture)
    return fixtures


def create_matchups(
    teams: list[models.Team], matchday: int, rotate: bool = False
) -> list[tuple[models.Team, models.Team]]:
    home, away = split_list(list_to_split=teams)
    matchups = list(zip(home, away, strict=True))
    if rotate:
        logging.info(f"rotating by {matchday}")
        _teams = deque(chain(*matchups))
        anchor = _teams.popleft()
        _teams.rotate(matchday)
        _teams.appendleft(anchor)
        home, away = split_list([*_teams])
        matchups = list(zip(home, away, strict=True))
    return matchups


def home_or_away(
    match: tuple[models.Team, models.Team],
    round_number: int,
):
    if round_number % 2 == 0:
        logging.info(
            f"Round {round_number} is even: H {match[0].name} vs. A {match[1].name}"
        )
        team_home = match[0]
        team_away = match[1]
    else:
        logging.info(
            f"Round {round_number} is odd: H {match[1].name} vs. A {match[0].name}"
        )
        team_home = match[1]
        team_away = match[0]
    return team_home, team_away


def add_bye_week_team(
    schedule: models.Schedule, teams: list[models.Team]
) -> list[models.Team]:
    """
    If number of teams is odd, create a "Bye" team to ensure scheduling
    accounts for a bye week.
    """
    if len(teams) % 2 != 0:
        teams.append(models.Team(name="BYE", league_id=schedule.league_id))
    return teams


def split_list(
    list_to_split: list[models.Team]
) -> tuple[list[models.Team], list[models.Team]]:
    """Split a list of teams in half, raising an error if the list is odd."""
    if len(list_to_split) % 2 != 0:
        raise ValueError("List length must be even.")

    return (
        list_to_split[: len(list_to_split) // 2],
        list_to_split[len(list_to_split) // 2 :],
    )


def weekly_increment(schedule: models.Schedule, num_weeks: int = 1) -> datetime:
    if not num_weeks:
        return schedule.scheduled_start
    increment_by = num_weeks
    return schedule.scheduled_start + timedelta(weeks=increment_by)


def determine_time(
    schedule: models.Schedule, start_time: datetime, count: int, match_count: int
):
    if count == 1 or count <= schedule.concurrent_games:
        return start_time
    minute_increment = schedule.time_between_games * (count - 1)
    return start_time + timedelta(minutes=minute_increment)


def determine_field(
    schedule: models.Schedule, count: int, initial_field: int = 1
) -> int:
    if count == 1 or count > schedule.concurrent_games:
        return initial_field
    return initial_field + count - 1
