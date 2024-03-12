import pytest
from litestar.testing import AsyncTestClient


@pytest.mark.anyio
async def test_health_check(app: AsyncTestClient):
    response = await app.get("/")
    assert response.status_code == 200
