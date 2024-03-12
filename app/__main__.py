from . import __app_name__, cli
from .core import get_app_settings

settings = get_app_settings()


def main():
    cli.iesl_cli(prog_name=__app_name__)


if __name__ == "__main__":
    main()

