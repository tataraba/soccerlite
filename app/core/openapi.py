from litestar.openapi.config import OpenAPIConfig

from . import get_app_settings

settings = get_app_settings()


if settings.DISABLE_OPENAPI:
    config = None
else:
    config = OpenAPIConfig(
        title=settings.NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        external_docs=settings.EXTERNAL_DOCS,  # type: ignore[arg-type]
        use_handler_docstrings=True,
        root_schema_site="swagger",
    )
