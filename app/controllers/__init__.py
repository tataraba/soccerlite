# from litestar.contrib.htmx.request import HTMXRequest
from litestar.types import ControllerRouterHandler

from .admin import (
    AdminFixtureController,
    AdminLeagueController,
    AdminScheduleController,
    AdminSeasonController,
    AdminTeamController,
)
from .iesl import LeagueController
from .web import WebController

__all__ = [
    "routes",
    "WebController",
    "LeagueController",
    "AdminLeagueController",
    "AdminSeasonController",
    "AdminTeamController",
    "AdminScheduleController",
]

routes: list[ControllerRouterHandler] = [
    LeagueController,
    WebController,
    AdminLeagueController,
    AdminSeasonController,
    AdminTeamController,
    AdminScheduleController,
    AdminFixtureController,
]
