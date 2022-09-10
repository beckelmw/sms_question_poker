import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_equals(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}
