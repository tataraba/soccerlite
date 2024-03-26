from litestar import Controller, get
from litestar.contrib.htmx.request import HTMXRequest
from litestar.di import Provide
from litestar.response import Template

from app.controllers import urls
from app.core.response import htmx_template
from app.dto import LeagueDTO
from app.services import provide_league_repo, provide_schedule_service


class LeagueController(Controller):
    """Handles the interactions within the League objects."""

    dependencies = {"league_repo": Provide(provide_league_repo)}
    return_dto = LeagueDTO

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
