from typing import Any, Protocol, Type, TypeVar
from uuid import UUID

from fastapi import Depends
from sqlmodel import SQLModel, select

from .db import AsyncSession, get_session

T = TypeVar("T", bound=SQLModel)


class RepositoryProtocol(Protocol[T]):
    async def findOne(self, reference: Any) -> T | None:
        ...

    async def find(self, reference: Any) -> list[T]:
        ...

    async def get(self, id: UUID) -> T | None:
        ...

    async def add(self, item: T) -> T:
        ...

    async def update(self, item: T, data: T) -> T | None:
        ...

    async def delete(self, item: T) -> bool:
        ...


class Repository(RepositoryProtocol[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def __call__(
        self, session: AsyncSession = Depends(get_session)
    ) -> RepositoryProtocol[T]:
        self.session = session
        return self

    async def findOne(self, reference: Any) -> T | None:
        results = await self.session.execute(select(self.model).where(reference))
        item: T | None = results.scalar_one_or_none()
        return item

    async def find(self, reference: Any) -> list[T]:
        results = await self.session.execute(select(self.model).where(reference))
        return results.scalars().all()

    async def get(self, id: UUID) -> T | None:
        return await self.session.get(self.model, id)

    async def add(self, item: T) -> T:
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update(self, item: T, data: T) -> T | None:
        values = data.dict(exclude_unset=True)

        for k, v in values.items():
            setattr(item, k, v)

        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)

        return item

    async def delete(self, item: T) -> bool:
        await self.session.delete(item)
        await self.session.commit()
        return True
