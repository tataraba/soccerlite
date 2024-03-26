from litestar import Controller, get
from litestar.contrib.htmx.request import HTMXRequest
from litestar.response import Template
from litestar.status_codes import HTTP_200_OK

from app.core.response import htmx_template

from . import urls


class WebController(Controller):
    @get(
        [urls.INDEX],
        status_code=HTTP_200_OK,
        name="iesl:index",
        include_in_schema=False,
    )
    async def home(self, request: HTMXRequest) -> Template:
        return htmx_template(template_name="main.html")

    # @get(
    #     [urls.ACCOUNT_LOGIN],
    #     status_code=HTTP_200_OK,
    #     name="login",
    #     include_in_schema=False,
    # )
    # async def login(self, request: HTMXRequest) -> Template:
    #     htmx = request.htmx
    #     print(htmx.target)
    #     return htmx_template(template_name="login.html")
