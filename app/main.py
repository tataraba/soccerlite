from __future__ import annotations

from typing import TYPE_CHECKING

from .core import (
    get_app_settings,
    log,
    openapi,
    plugin,
    response,
    static_files,
)

if TYPE_CHECKING:
    from litestar import Litestar

__all__ = ["create_app", "app"]


def create_app() -> Litestar:
    get_app_settings.cache_clear()
    # log.setup_rich_logger()

    from litestar import Litestar
    from litestar.contrib.htmx.request import HTMXRequest

    from app import controllers

    return Litestar(
        request_class=HTMXRequest,
        debug=True,  # type: ignore
        response_class=response.htmx_template,
        route_handlers=[*controllers.routes],
        template_config=response.template_config,
        static_files_config=static_files.config,
        openapi_config=openapi.config,
        plugins=[plugin.db_plugin, plugin.users_plugin],
        logging_config=log.logger_config,
    )


app = create_app()
