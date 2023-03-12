from asyncio import current_task
from sqlalchemy.ext.asyncio import async_scoped_session, create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from api.config import DB_URL


async_engine = create_async_engine(DB_URL, echo=True)
async_session = async_scoped_session(
    async_sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=async_engine
    ), scopefunc=current_task
)

Base = declarative_base()


async def get() -> AsyncSession:
    async with async_session() as session:
        yield session
