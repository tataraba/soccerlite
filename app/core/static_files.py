from litestar.static_files.config import StaticFilesConfig

from .config import get_app_settings

settings = get_app_settings()

config = [
    StaticFilesConfig(
        directories=[settings.STATIC_DIR],
        path=settings.STATIC_URL,
        name="static",
        html_mode=True,
        opt={"exclude_from_auth": True, "skip_rate_limiting": True},
    ),
]
