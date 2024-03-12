import json
import logging
from pathlib import Path

from litestar.logging import LoggingConfig
from rich.logging import RichHandler

from . import get_app_settings

settings = get_app_settings()

LOGGER_LEVEL: int = settings.LOG_LEVEL
DATE_FORMAT: str = r"%d %b %Y | %H:%M:%S"
MICROSECOND_FORMAT: str = "%s.%03dZ"
SHELL_FORMAT: str = "%(asctime)s | %(message)s"
FILE_FORMAT: str = (
    "%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s"
)
JSON_FORMAT: dict[str, str] = {
    "level": "levelname",
    "message": "message",
    "loggerName": "name",
    "processName": "processName",
    "processID": "process",
    "threadName": "threadName",
    "threadID": "thread",
    "timestamp": "asctime",
    "functionName": "funcName",
}

settings.LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGER_FILE: Path = Path(settings.LOG_DIR / settings.LOG_FILENAME)
LOGGER_FILE_MODE: str = settings.LOG_FILE_MODE


class JsonFormatter(logging.Formatter):
    """Formatter for JSON log messages.

    Reference:
    https://stackoverflow.com/questions/50144628/python-logging-into-file-as-a-dictionary-or-json
    """

    def __init__(
        self,
        fmt_dict: dict[str, str] | None = None,
        time_format: str = DATE_FORMAT,
        msec_format: str = MICROSECOND_FORMAT,
    ):
        super().__init__(fmt=FILE_FORMAT, datefmt=time_format)
        self.fmt_dict = fmt_dict if fmt_dict is not None else {"message": "message"}
        self.default_time_format = time_format
        self.default_msec_format = msec_format
        self.datefmt = None

    def usesTime(self) -> bool:
        return "asctime" in self.fmt_dict.values()

    def formatMessage(self, record):
        """Overwritten to return a dictionary of the relevant LogRecord attributes
        instead of a string. KeyError is raised if an unknown attribute is provided
        in the fmt_dict.
        """
        return {
            fmt_key: record.__dict__[fmt_val]
            for fmt_key, fmt_val in self.fmt_dict.items()
        }

    def format(self, record: logging.LogRecord) -> str:
        """Format the log message as JSON."""
        record.message = record.getMessage()

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        message_dict = self.formatMessage(record)

        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            message_dict["exc_info"] = record.exc_text

        if record.stack_info:
            message_dict["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(message_dict)


shell_handler = RichHandler(
    rich_tracebacks=True, tracebacks_show_locals=True, show_time=False
)

logger_config = LoggingConfig(
    root={
        "level": logging.getLevelName(logging.INFO),
        "handlers": [
            "json_handler",
            "console",
        ],
    },
    formatters={
        "standard": {
            "format": SHELL_FORMAT,
            "datefmt": DATE_FORMAT,
        },
        "json_formatter": {
            "()": "app.core.log.JsonFormatter",
            "fmt_dict": JSON_FORMAT,
        },
    },
    handlers={
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "standard",
            "rich_tracebacks": True,
            "tracebacks_show_locals": True,
            "show_time": False,
        },
        "json_handler": {
            "class": "logging.FileHandler",
            "formatter": "json_formatter",
            "level": logging.getLevelName(LOGGER_LEVEL),
            "filename": LOGGER_FILE,
            "mode": LOGGER_FILE_MODE,
        },
    },
    log_exceptions="always",
)
