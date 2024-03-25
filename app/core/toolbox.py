import logging
import re
import unicodedata
from datetime import datetime, timezone
from importlib.util import find_spec
from pathlib import Path
from zoneinfo import ZoneInfo

from dateutil import tz


def module_to_os_path(module_name: str) -> str:
    """Get the string path of the module."""
    spec = find_spec(module_name)
    if not spec:
        raise ValueError(f"Couldn't find path for {module_name}")
    return str(Path(spec.origin).parent)  # type: ignore[arg-type]


def slugify(
    value: str, allow_unicode: bool = False, separator: str | None = None
) -> str:
    """slugify.

    Convert to ASCII if ``allow_unicode`` is ``False``. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    Args:
        value (str): the string to slugify
        allow_unicode (bool, optional): allow unicode characters in slug. Defaults to False.
        separator (str, optional): by default a `-` is used to delimit word boundaries.
            Set this to configure something different.

    Returns:
        str: a slugified string of the value parameter
    """
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    if separator is not None:
        return re.sub(r"[-\s]+", "-", value).strip("-_").replace("-", separator)
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def convert_utc_to_pst(utc_datetime: datetime) -> datetime:
    LOS_ANGELES = tz.gettz("America/Los_Angeles")
    _utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    converted_datetime = _utc_datetime.astimezone(LOS_ANGELES)
    return converted_datetime.replace(fold=1)
