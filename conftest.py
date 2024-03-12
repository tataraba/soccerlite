from __future__ import annotations

import asyncio
import re
from typing import TYPE_CHECKING, Any, AsyncIterator
from unittest.mock import MagicMock

import pytest
from app.core import config
from httpx import AsyncClient
from litestar.testing import AsyncTestClient

if TYPE_CHECKING:
    from collections import abc
    from collections.abc import Iterator

    from app.models import League, Schedule, Season, Team
    from pytest import FixtureRequest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(name="app")
async def fx_app() -> AsyncIterator[AsyncClient]:
    from app.main import app

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(name="seasons")
def fx_seasons() -> list[Season | dict[str, Any]]:
    return [
        {
            "name": "Season 1",
            "start_date": "2022-01-01",
        },
        {
            "name": "Season 2",
            "slug": "season-2",
            "start_date": "2022-02-01",
        },
        {
            "name": "Season 3",
            "slug": "season-3",
            "start_date": "2022-03-01",
            "end_date": "2022-04-01",
        },
    ]


@pytest.fixture(name="leagues")
def fx_leagues() -> list[League | dict[str, Any]]:
    return [
        {
            "name": "League 1",
            "category": "Men's",
            "team_size": 11,
            "day_of_week": "Sunday",
            "male_age_over": 30,
        },
        {
            "name": "League 1",
            "category": "Women's",
            "team_size": 7,
            "day_of_week": "Monday",
        },
        {
            "name": "League 1",
            "category": "Women's",
            "team_size": 7,
            "day_of_week": "Monday",
        },
    ]
