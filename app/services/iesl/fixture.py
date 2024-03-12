import logging
from collections import deque
from datetime import datetime, timedelta
from random import shuffle
from typing import Any
from uuid import UUID

from advanced_alchemy import FilterTypes
from advanced_alchemy.filters import OrderBy
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
        start_date: datetime | None = None,
        **kwargs: Any,
    ):
        """
        Generate fixtures for a schedule taking the number
        of games from the schedule, as well as the teams
        that are registered to the league.
        """
        if not start_date:
            start_date = datetime.now()
        if len(teams) % 2 != 0:
            teams.append(models.Team(name="BYE", league_id=schedule.league_id))

        shuffle(teams)  # Randomizes matchups to vary between seasons
        home, away = split_list(teams)
        flatten_teams = deque(away)
        flatten_teams.extend(reversed(home))
        anchor_team = flatten_teams.pop()
        fixtures = []
        fixture_teams = []
        # First matchday, create fixtures based on "zipping" the home and away teams
        for matchday in range(len(teams) - 1):
            if matchday == 0:
                matches = list(zip(home, away, strict=True))
                _fixtures, _fixture_teams = matchday_fixtures(
                    matches=matches,
                    schedule=schedule,
                    matchday=matchday + 1,
                    matchday_date=start_date,
                )
                fixtures.extend(_fixtures)
                fixture_teams.extend(_fixture_teams)
            # Subsequent matchdays, create fixtures based on the rotation of the teams
            else:
                matches = rotate_and_match_teams(anchor_team, flatten_teams)
                shuffle(matches)  # Randomizes start times for matches
                start_date = weekly_increment(start_date=start_date)
                _fixtures, _fixture_teams = matchday_fixtures(
                    matches=matches,
                    schedule=schedule,
                    matchday=matchday + 1,
                    matchday_date=start_date,
                )
                fixtures.extend(_fixtures)
                fixture_teams.extend(_fixture_teams)
                flatten_teams.pop()

        await self.create_many(fixture_teams, auto_commit=True, auto_expunge=True)

        return fixtures, fixture_teams


def split_list(list_to_split: list[Any]) -> tuple[list[Any], list[Any]]:
    """Split a list in half, raising an error if the list is odd."""
    if len(list_to_split) % 2 != 0:
        raise ValueError("List length must be even.")

    return (
        list_to_split[: len(list_to_split) // 2],
        list_to_split[len(list_to_split) // 2 :],
    )


def weekly_increment(start_date: datetime, num_weeks: int = 1) -> datetime:
    if num_weeks:
        increment_by = num_weeks
    return start_date + timedelta(weeks=increment_by)


def game_date_start(game_time: datetime, minute_increment: int) -> datetime:
    if minute_increment:
        game_time = game_time + timedelta(minutes=minute_increment)
        return game_time
    return game_time


def determine_field(schedule: models.Schedule, field: int, match_count: int) -> int:
    if match_count == 1:
        return field
    if match_count > schedule.concurrent_games:
        return field
    else:
        return field + 1


def determine_match_start_time(
    schedule: models.Schedule,
    matchday_date: datetime,
    match_count: int,
) -> datetime:
    if match_count <= schedule.concurrent_games:
        logging.info(
            f"Matchday date: {matchday_date}, match_count: {match_count} less than concurrent games: {schedule.concurrent_games}"
        )
        return matchday_date
    minute_increment = schedule.time_between_games * match_count
    logging.info(
        f"match count is equal or greater than concurrent games, adding {minute_increment} minutes"
    )
    return matchday_date + timedelta(minutes=minute_increment)


def rotate_and_match_teams(
    anchor_team: models.Team, team_bucket: deque
) -> list[tuple[models.Team, models.Team]]:
    """
    To create a list of matches for a particular match day, provide the `anchor_team`
    which should not be included in the `team_bucket` deque of teams that are to be scheduled.
    The `team_bucket` will be rotated once, and then the `anchor_team` will be appended. Next,
    the deque will be split in half, and the matches will be generated by zipping the two
    resulting lists.

    Args:
        anchor_team (str): The team that should not be included in the `team_bucket` deque.
        team_bucket (deque): The deque of teams that are to be scheduled.
    """
    team_bucket.rotate()
    team_bucket.rotate()
    team_bucket.append(anchor_team)
    home, away = split_list(list(team_bucket))
    away.reverse()
    return list(zip(home, away, strict=True))


def matchday_fixtures(
    *,
    matches: list[tuple[models.Team, models.Team]],
    schedule: models.Schedule,
    matchday: int,
    matchday_date: datetime,
) -> tuple[list[models.Fixture], list[models.FixtureTeam]]:
    fixtures = []
    fixture_teams = []
    field = 1

    for count, match in enumerate(matches, start=1):
        logging.info(
            f"count: {count}, matchday: {matchday}, conc: {schedule.concurrent_games}"
        )
        game_date = determine_match_start_time(
            schedule=schedule, matchday_date=matchday_date, match_count=count
        )
        field = determine_field(schedule=schedule, field=field, match_count=count)
        logging.info(f"field: {field} - game_date: {game_date}")
        fixture = models.Fixture(
            schedule_id=schedule.id,
            team_home=match[0].id,
            team_away=match[1].id,
            team_home_name=match[0].name,
            team_away_name=match[1].name,
            matchday=matchday,
            game_date=game_date,
            field=field,
            game_status=models.FixtureStatus.UNPLAYED,
        )

        fixture_team_home = models.FixtureTeam(team=match[0], fixture=fixture)
        fixture_team_away = models.FixtureTeam(team=match[1], fixture=fixture)
        fixture_teams.extend([fixture_team_home, fixture_team_away])

        fixture.teams.extend([fixture_team_home, fixture_team_away])
        fixtures.append(fixture)

    return fixtures, fixture_teams
