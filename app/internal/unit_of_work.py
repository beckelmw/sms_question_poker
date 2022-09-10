from contextlib import AbstractAsyncContextManager
from typing import Any, Generic, TypeVar

from sqlmodel import SQLModel

from .db import AsyncSession
from .repository import RepositoryProtocol

T = TypeVar("T", bound=SQLModel)


class UnitOfWork(Generic[T], AbstractAsyncContextManager):
    def __init__(self, session: AsyncSession, repository: RepositoryProtocol[T]):
        self.session = session
        self.repo = repository

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, *args: Any) -> None:
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
