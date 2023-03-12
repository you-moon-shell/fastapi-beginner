import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from api.models import Base
from api.config import DB_URL


async_engine = create_async_engine(DB_URL, echo=True, poolclass=NullPool)


async def _reset() -> None:
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


def run() -> None:
    asyncio.run(_reset())
