from litestar import Controller, get
from litestar.contrib.htmx.request import HTMXRequest
from litestar.di import Provide
from litestar.response import Template
from litestar.status_codes import HTTP_200_OK

from app.controllers import urls
from app.core.response import htmx_template
from app.core.toolbox import convert_utc_to_pst
from app.dto import LeagueDTO, LeagueReadDTO
from app.services import provide_fixture_repo, provide_league_repo, provide_team_repo
from app.services.iesl import FixtureRepo, LeagueRepo, TeamRepo


class LeagueController(Controller):
    """Handles the interactions within the League objects."""

    dependencies = {
        "league_repo": Provide(provide_league_repo),
        "fixture_repo": Provide(provide_fixture_repo),
        "teams_repo": Provide(provide_league_repo),
    }
    return_dto = LeagueDTO

    @get(
        [urls.SCHEDULE_INDEX],
        status_code=HTTP_200_OK,
        name="schedules",
        dependencies={
            "league_repo": provide_league_repo,
            "fixture_repo": provide_fixture_repo,
            "teams_repo": provide_team_repo,
        },
        include_in_schema=False,
        dto=LeagueReadDTO,
    )
    async def schedules(
        self,
        request: HTMXRequest,
        league_repo: LeagueRepo,
        fixture_repo: FixtureRepo,
        teams_repo: TeamRepo,
    ) -> Template:
        leagues = await league_repo.list()
        rows = await fixture_repo.upcoming_fixtures()
        teams = await teams_repo.list()
        return htmx_template(
            template_name="iesl/schedules.html",
            context={
                "leagues": leagues,
                "rows": rows,
                "utc_to_pst": convert_utc_to_pst,
                "teams": teams,
            },
        )

    @get(
        [urls.LEAGUE_INDEX],
        name="league",
    )
    async def league_home(self, request: HTMXRequest) -> Template:
        print("here be some info")
        return htmx_template(template_name="main.html")

    @get(
        [urls.LEAGUE_SCHEDULE],
        name="league_schedule",
    )
    async def league_schedule(self, request: HTMXRequest) -> Template:
        return htmx_template(template_name="main.html")

    @get(
        [urls.LEAGUE_STANDINGS],
        name="league_standings",
    )
    async def league_standings(self, request: HTMXRequest) -> Template:
        return htmx_template(template_name="main.html")

    # @get(
    #     [urls.LEAGUE_STATS],
    #     name="league_stats",
    # )
    # async def league_stats(self, request: HTMXRequest) -> Template:
    #     return htmx_template(template_name="main.html")
