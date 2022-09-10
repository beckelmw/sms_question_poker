from sys import modules
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..settings import Settings

settings = Settings()

db_connection_str = settings.DATABASE_URL

if "pytest" in modules:
    db_connection_str = settings.DATABASE_URL_TEST

async_engine = create_async_engine(
    db_connection_str,
    echo=True,
    future=True,
    # https://community.fly.io/t/postgresql-connection-is-closed-error-after-a-few-minutes-of-activity/4768/7
    pool_recycle=1200,
)


async def get_session() -> AsyncGenerator:
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
