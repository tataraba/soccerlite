import logging

import typer

from . import db
from .core import get_app_settings

settings = get_app_settings()
logger = logging.getLogger(__name__)

iesl_cli = typer.Typer()


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    message = f"{settings.NAME} {settings.VERSION}\n"
    print(message)
    raise typer.Exit()


@iesl_cli.command()
def main(
    version: bool = typer.Option(  # noqa
        None,
        "--version",
        "-v",
        help="[bold green]Show the version and exit.[/bold green]",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    return


@iesl_cli.command(
    name="create-database",
    help="Creates an empty sqlite database and executes migrations",
)
def create_database() -> None:
    """Create database DDL migrations."""
    db.create_database()
