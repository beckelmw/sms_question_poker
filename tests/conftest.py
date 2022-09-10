import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.internal.db import async_engine
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:  # noqa: indirect usage
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://localhost:8000/") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture()
async def authorized_client(
    async_session: AsyncSession, async_client: AsyncClient
) -> AsyncClient:
    await async_client.post(
        "/signup",
        json={
            "username": "test@beckelman.net",
            "password": "pass@word",
            "first_name": "Test",
            "last_name": "User",
        },
    )

    response = await async_client.post(
        "/login",
        data={
            "username": "test@beckelman.net",
            "password": "pass@word",
            "grant_type": "password",
        },
    )

    json = response.json()

    async_client.headers.setdefault("authorization", f"bearer {json['access_token']}")
    return async_client
